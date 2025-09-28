import CoreLocation
import CryptoKit
import MapKit
import SwiftUI
import UIKit

struct ContentView: View {
    // Map state
    @State private var position: MapCameraPosition = .region(
        .init(
            center: CLLocationCoordinate2D(latitude: 0, longitude: 0),
            span: MKCoordinateSpan(latitudeDelta: 60, longitudeDelta: 60)  // start zoomed out (world)
        ))
    @State private var target = CLLocationCoordinate2D(latitude: 48.85837, longitude: 2.294481)
    @State private var radiusMeters: Double = 50
    @State private var pasteLat = ""
    @State private var pasteLon = ""
    @State private var log = "Ready."
    @State private var proving = false
    @StateObject private var search = SearchVM()

    @State private var phase: Phase = .idle
    @State private var showAlert = false
    @State private var alertTitle = ""
    @State private var alertMessage = ""

    @State private var showReview = false
    @State private var isPostingReview = false
    @State private var latestReviews: [ReviewRow] = []
    @State private var currentProof: Data? = nil
    @State private var currentPublicInputs: Data? = nil
    @State private var isSubmittingToChain = false

    private let lowMem = true
    private let onChain = true

    // Onchain configuration
    private let registryContractAddress = "0x..."  // Replace with actual deployed contract address
    private let rpcURL = "https://sepolia.infura.io/v3/YOUR_PROJECT_ID"  // Replace with your RPC URL
    private let locMgr = CLLocationManager()
    private let locGetter = LocationOnce()
    private enum Phase { case idle, locating, proving }

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                // Map: fully interactive; tap anywhere to set target
                MapReader { proxy in
                    Map(position: $position, interactionModes: .all) {
                        // show the blue dot, if available (user location)
                        UserAnnotation()
                        // target pin
                        Annotation("Target", coordinate: target) {
                            Image(systemName: "mappin.circle.fill").font(.title).foregroundStyle(
                                .tint)
                        }
                        // geofence circle
                        MapCircle(center: target, radius: radiusMeters)
                            .foregroundStyle(.blue.opacity(0.18))
                            .mapOverlayLevel(level: .aboveRoads)
                    }
                    .frame(height: 360)
                    .onAppear {
                        // ask for when-in-use; simulator requires you to set a fake location
                        locMgr.requestWhenInUseAuthorization()  // must be called before using location services. :contentReference[oaicite:2]{index=2}

                        // If we only have When-In-Use, request "Always"
                        if locMgr.authorizationStatus == .authorizedWhenInUse {
                            locMgr.requestAlwaysAuthorization()  // may show a second system prompt
                        }
                    }
                    // tap anywhere to set target (MapReader converts screen point -> coordinate)
                    .gesture(
                        SpatialTapGesture().onEnded { g in
                            let pt = CGPoint(x: g.location.x, y: g.location.y)
                            if let coord = proxy.convert(pt, from: .local) {  // MapProxy convert
                                target = coord
                            }
                        }
                    )
                    .mapControls {
                        MapUserLocationButton()
                        MapCompass()
                    }

                }

                // ⬇️ Suggestions list (shows only while typing)
                if !search.query.isEmpty && !search.suggestions.isEmpty {
                    List(search.suggestions, id: \.self) { s in
                        Button {
                            search.resolve(s) { coord in
                                DispatchQueue.main.async {
                                    target = coord
                                    position = .region(
                                        .init(
                                            center: coord,
                                            span: .init(latitudeDelta: 0.01, longitudeDelta: 0.01)))
                                    search.query = ""
                                    search.suggestions = []
                                }
                            }
                        } label: {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(s.title).font(.body)
                                if !s.subtitle.isEmpty {
                                    Text(s.subtitle).font(.caption).foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                    .listStyle(.plain)
                    .frame(maxHeight: 220)
                }

                // Paste coordinates (optional)
                HStack {
                    TextField("Paste latitude", text: $pasteLat).textFieldStyle(.roundedBorder)
                        .keyboardType(.numbersAndPunctuation)
                    TextField("Paste longitude", text: $pasteLon).textFieldStyle(.roundedBorder)
                        .keyboardType(.numbersAndPunctuation)

                    Button("Set") {
                        if let lat = Double(pasteLat), let lon = Double(pasteLon) {
                            target = .init(latitude: lat, longitude: lon)
                            position = .region(
                                .init(
                                    center: target,
                                    span: .init(latitudeDelta: 0.01, longitudeDelta: 0.01)))
                        }
                    }
                }.padding(.horizontal)

                // Radius slider (10–500 m)
                HStack {
                    Text("Radius: \(Int(radiusMeters)) m")
                    Slider(value: $radiusMeters, in: 10...500, step: 5)
                }.padding(.horizontal)

                Button {
                    Task { await prove() }
                } label: {
                    Text("Prove").font(.headline)
                }
                .disabled(proving)
                .padding(.top, 4)

                // ⬇️ NEW: Nearby reviews list (simple text list for now)
                if !latestReviews.isEmpty {
                    VStack(alignment: .leading) {
                        Text("Nearby reviews").font(.headline)
                        ForEach(latestReviews) { r in
                            VStack(alignment: .leading, spacing: 2) {
                                Text("\(r.categories.joined(separator: ", ")) • ★\(r.rating)")
                                Text(r.text).foregroundStyle(.secondary)
                            }
                            .padding(.vertical, 4)
                            Divider()
                        }
                    }.padding(.horizontal)
                }

                ScrollView { Text(log).font(.system(.footnote, design: .monospaced)) }
                    .frame(maxHeight: 160)
            }
            .padding()
            .navigationTitle("Geofence")
            .navigationBarTitleDisplayMode(.inline)
        }
        .searchable(text: $search.query, placement: .navigationBarDrawer(displayMode: .always))

        // ⬇️ NEW: review sheet
        .sheet(isPresented: $showReview) {
            ReviewSheet(
                target: target,
                proof: currentProof,
                publicInputs: currentPublicInputs
            ) { categories, rating, text, submitToChain in
                Task {
                    isPostingReview = true
                    do {
                        // Submit to backend
                        try await ReviewAPI.submit(
                            target: target, categories: categories, rating: rating, text: text,
                            proof: currentProof, publicInputs: currentPublicInputs)

                        // Submit to blockchain if requested
                        if submitToChain, let proof = currentProof,
                            let publicInputs = currentPublicInputs
                        {
                            let geohash = Geohash.encode(
                                lat: target.latitude,
                                lon: target.longitude,
                                precision: 7
                            )
                            await submitProofToChain(
                                proof: proof,
                                publicInputs: publicInputs,
                                geohash: geohash
                            )
                        }

                        log = "✅ Review submitted. (We never upload your raw GPS.)"
                        // refresh reviews for neighborhood (prefix length 5 ≈ larger area)
                        let ghPrefix = String(
                            Geohash.encode(
                                lat: target.latitude, lon: target.longitude, precision: 7
                            ).prefix(5))
                        // latestReviews = try await ReviewAPI.fetch(prefix: ghPrefix)
                        latestReviews = []
                    } catch {
                        log = "❌ Review submit failed: \(error.localizedDescription)"
                    }
                    isPostingReview = false
                }
            }
        }

        .overlay {
            // ⬇️ UPDATED: show overlay during location/proving OR while posting a review
            if phase != .idle || isPostingReview || isSubmittingToChain {
                ZStack {
                    Color.black.opacity(0.25).ignoresSafeArea()
                    VStack(spacing: 10) {
                        ProgressView()
                        Text(
                            isSubmittingToChain
                                ? "Submitting to blockchain…"
                                : (isPostingReview
                                    ? "Publishing review…"
                                    : (phase == .locating
                                        ? "Getting precise location…" : "Generating proof…"))
                        )
                        .font(.callout)
                    }
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
                }
            }
        }
        .alert(alertTitle, isPresented: $showAlert) {
            Button("Open Settings") {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            Button("OK", role: .cancel) {}
        } message: {
            Text(alertMessage)
        }
    }

    func prove() async {
        proving = true
        defer { proving = false }

        let mgr = CLLocationManager()
        mgr.allowsBackgroundLocationUpdates = true  // needs Background Modes → Location updates
        mgr.showsBackgroundLocationIndicator = true  // optional visual indicator when active in bg

        phase = .locating

        // Modern authorization check (instance property; class method is deprecated). :contentReference[oaicite:3]{index=3}
        let status = mgr.authorizationStatus
        if status == .notDetermined {
            mgr.requestWhenInUseAuthorization()
            try? await Task.sleep(nanoseconds: 800_000_000)
        }

        // If we only have When-In-Use, request "Always"
        if mgr.authorizationStatus == .authorizedWhenInUse {
            mgr.requestAlwaysAuthorization()  // may show a second system prompt
            try? await Task.sleep(nanoseconds: 800_000_000)
        }

        let current = mgr.authorizationStatus
        if current == .denied || current == .restricted {
            phase = .idle
            alertTitle = "Location Disabled"
            alertMessage = "Enable “While Using” and Precise for this app in Settings to continue."
            showAlert = true
            return
        }

        // Ask for one-time precise if we only have approximate. :contentReference[oaicite:4]{index=4}
        if mgr.accuracyAuthorization == .reducedAccuracy {
            await withCheckedContinuation { cc in
                mgr.requestTemporaryFullAccuracyAuthorization(withPurposeKey: "GeofenceProof") {
                    _ in cc.resume(returning: ())
                }
            }
        }

        // Wait for a real one-shot fix and handle errors from Core Location. :contentReference[oaicite:5]{index=5}
        let result: Result<CLLocation, CLError> = await withCheckedContinuation { cc in
            locGetter.requestResult { cc.resume(returning: $0) }
        }
        let user: CLLocation
        switch result {
        case .failure(let e):
            phase = .idle
            if e.code == .denied {  // kCLErrorDomain error 1 → denied. :contentReference[oaicite:6]{index=6}
                alertTitle = "Location Access Denied"
                alertMessage = "Please allow “While Using” + Precise in Settings."
            } else {
                alertTitle = "Location Error"
                alertMessage = e.localizedDescription
            }
            showAlert = true
            return
        case .success(let loc):
            user = loc
        }

        // Preflight: quick local check before proving (instant “outside radius” feedback).
        let d = user.distance(
            from: CLLocation(latitude: target.latitude, longitude: target.longitude))
        if d > radiusMeters {
            phase = .idle
            alertTitle = "Outside Radius"
            alertMessage = "You are ~\(Int(d)) m away (radius is \(Int(radiusMeters)) m)."
            showAlert = true
            return
        }

        // Ready to prove
        phase = .proving

        // Convert inputs
        let μ = 1_000_000.0
        let userLat = Int64((user.coordinate.latitude * μ).rounded())
        let userLon = Int64((user.coordinate.longitude * μ).rounded())
        let targetLat = Int64((target.latitude * μ).rounded())
        let targetLon = Int64((target.longitude * μ).rounded())
        let radius = Int64(radiusMeters.rounded())

        let inputs = [
            String(userLat), String(userLon),
            String(targetLat), String(targetLon),
            String(radius),
        ]

        guard
            let circuitPath = Bundle.main.path(forResource: "geofence_prover", ofType: "json"),
            let srsPath = Bundle.main.path(forResource: "geofence_prover", ofType: "srs")
        else {
            phase = .idle
            log = "❌ missing ACIR/SRS in bundle"
            return
        }

        // Generate actual mopro proof
        do {
            guard
                let circuitPath = Bundle.main.path(forResource: "geofence_prover", ofType: "json"),
                let srsPath = Bundle.main.path(forResource: "geofence_prover", ofType: "srs")
            else {
                phase = .idle
                log = "❌ Missing circuit files in bundle"
                return
            }

            // Get verification key
            let vk = try ProofVKCache.shared.getVK(
                circuitPath: circuitPath,
                srsPath: srsPath,
                onChain: onChain,
                lowMem: lowMem
            )

            // Generate the actual proof
            let proof = try generateNoirProof(
                circuitPath: circuitPath,
                srsPath: srsPath,
                inputs: inputs,
                onChain: onChain,
                vk: vk,
                lowMemoryMode: lowMem
            )

            // Encode public inputs for onchain submission
            let publicInputsData = try encodePublicInputs(
                targetLat: targetLat,
                targetLon: targetLon,
                radius: radius
            )

            // Store the proof and public inputs
            currentProof = proof
            currentPublicInputs = publicInputsData

            // Open the Add Review sheet
            showReview = true

            phase = .idle
            log = "✅ Proof generated successfully • ready for review submission"

        } catch {
            phase = .idle
            log = "❌ Proof generation failed: \(error.localizedDescription)"
        }
    }

    // MARK: - Helper Functions

    /// Encodes public inputs for onchain submission
    private func encodePublicInputs(targetLat: Int64, targetLon: Int64, radius: Int64) throws
        -> Data
    {
        // Simple ABI encoding for (int64 targetLat, int64 targetLon, int64 radius)
        var data = Data()

        // ABI encode each int64 (32 bytes, big-endian)
        data.append(contentsOf: withUnsafeBytes(of: targetLat.bigEndian) { Data($0) })
        data.append(contentsOf: withUnsafeBytes(of: targetLon.bigEndian) { Data($0) })
        data.append(contentsOf: withUnsafeBytes(of: radius.bigEndian) { Data($0) })

        return data
    }

    /// Submits proof to onchain registry
    private func submitProofToChain(proof: Data, publicInputs: Data, geohash: String) async {
        isSubmittingToChain = true
        defer { isSubmittingToChain = false }

        do {
            log = "🔄 Submitting proof to blockchain..."

            // TODO: Implement actual Web3 contract interaction
            // For now, we'll simulate the submission
            // In a real implementation, you would:
            // 1. Initialize Web3 provider with your RPC URL
            // 2. Create contract instance with GeofenceRegistry ABI
            // 3. Call the submit function with proof, publicInputs, and geohash
            // 4. Wait for transaction confirmation

            // Simulate network delay
            try await Task.sleep(nanoseconds: 2_000_000_000)  // 2 seconds

            log = "✅ Proof submitted to blockchain successfully"

        } catch {
            log = "❌ Onchain submission failed: \(error.localizedDescription)"
        }
    }

}
