import SwiftUI
import MapKit
import CoreLocation
// import MoproFFI
import CryptoKit

struct ContentView: View {
    // Map state
    @State private var position: MapCameraPosition = .region(.init(
        center: CLLocationCoordinate2D(latitude: 0, longitude: 0),
        span: MKCoordinateSpan(latitudeDelta: 60, longitudeDelta: 60)   // start zoomed out (world)
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

    private let lowMem = true
    private let onChain = true
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
                        Image(systemName: "mappin.circle.fill").font(.title).foregroundStyle(.tint)
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
                }
                // tap anywhere to set target (MapReader converts screen point -> coordinate)
                .gesture(SpatialTapGesture().onEnded { g in
                    let pt = CGPoint(x: g.location.x, y: g.location.y)
                    if let coord = proxy.convert(pt, from: .local) {  // MapProxy convert
                        target = coord
                    }
                })
                    .mapControls { MapUserLocationButton(); MapCompass() }

            }

            // ⬇️ Suggestions list (shows only while typing)
if !search.query.isEmpty && !search.suggestions.isEmpty {
    List(search.suggestions, id: \.self) { s in
        Button {
            search.resolve(s) { coord in
    DispatchQueue.main.async {
        target = coord
        position = .region(.init(center: coord, span: .init(latitudeDelta: 0.01, longitudeDelta: 0.01)))
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
                TextField("Paste latitude", text: $pasteLat).textFieldStyle(.roundedBorder).keyboardType(.numbersAndPunctuation)
                TextField("Paste longitude", text: $pasteLon).textFieldStyle(.roundedBorder).keyboardType(.numbersAndPunctuation)

                Button("Set") {
                    if let lat = Double(pasteLat), let lon = Double(pasteLon) {
                        target = .init(latitude: lat, longitude: lon)
                        position = .region(.init(center: target, span: .init(latitudeDelta: 0.01, longitudeDelta: 0.01)))
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
                Text("Prove geofence").font(.headline)
            }
            .disabled(proving)
            .padding(.top, 4)

            ScrollView { Text(log).font(.system(.footnote, design: .monospaced)) }
                .frame(maxHeight: 160)
        }
        .padding().navigationTitle("Prove geofence")
        }
        .searchable(text: $search.query, placement: .navigationBarDrawer(displayMode: .always))
        .overlay {
    if phase != .idle {
        ZStack {
            Color.black.opacity(0.25).ignoresSafeArea()
            VStack(spacing: 10) {
                ProgressView()
                Text(phase == .locating ? "Getting precise location…" : "Generating proof…")
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
    phase = .locating

    // Modern authorization check (instance property; class method is deprecated). :contentReference[oaicite:3]{index=3}
    let status = mgr.authorizationStatus
    if status == .notDetermined {
        mgr.requestWhenInUseAuthorization()
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
            mgr.requestTemporaryFullAccuracyAuthorization(withPurposeKey: "GeofenceProof") { _ in cc.resume(returning: ()) }
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
        if e.code == .denied {                       // kCLErrorDomain error 1 → denied. :contentReference[oaicite:6]{index=6}
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
    let d = user.distance(from: CLLocation(latitude: target.latitude, longitude: target.longitude))
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
    let userLat   = Int64((user.coordinate.latitude  * μ).rounded())
    let userLon   = Int64((user.coordinate.longitude * μ).rounded())
    let targetLat = Int64((target.latitude  * μ).rounded())
    let targetLon = Int64((target.longitude * μ).rounded())
    let radius    = Int64(radiusMeters.rounded())

    let inputs = [
        String(userLat), String(userLon),
        String(targetLat), String(targetLon),
        String(radius)
    ]

    guard
        let circuitPath = Bundle.main.path(forResource: "geofence_prover", ofType: "json"),
        let srsPath     = Bundle.main.path(forResource: "geofence_prover", ofType: "srs")
    else { phase = .idle; log = "❌ missing ACIR/SRS in bundle"; return }

    do {
        let vk = try ProofVKCache.shared.getVK(
            circuitPath: circuitPath, srsPath: srsPath,
            onChain: onChain, lowMem: lowMem
        )
        let proof = try generateNoirProof(
            circuitPath: circuitPath, srsPath: srsPath,
            inputs: inputs, onChain: onChain, vk: vk, lowMemoryMode: lowMem
        )
        let ok = try verifyNoirProof(
            circuitPath: circuitPath, proof: proof,
            onChain: onChain, vk: vk, lowMemoryMode: lowMem
        )
        phase = .idle
        log = "✅ proof bytes: \(proof.count) • verified: \(ok)"
    } catch {
        phase = .idle
        log = "❌ \(error)"
    }
}


}
