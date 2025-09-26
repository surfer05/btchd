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

    private let lowMem = true
    private let onChain = true
    private let locMgr = CLLocationManager()

    var body: some View {
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
            }

            // Paste coordinates (optional)
            HStack {
                TextField("Paste latitude", text: $pasteLat).textFieldStyle(.roundedBorder)
                TextField("Paste longitude", text: $pasteLon).textFieldStyle(.roundedBorder)
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
        .padding()
    }

    // MARK: - Proof flow (unchanged from earlier)
    func prove() async {
        proving = true
        defer { proving = false }

        // If Approximate was granted, ask once for temporary precise using your purpose key (Info.plist)
        if CLLocationManager().accuracyAuthorization == .reducedAccuracy {
            await withCheckedContinuation { cc in
                CLLocationManager().requestTemporaryFullAccuracyAuthorization(withPurposeKey: "GeofenceProof") { _ in cc.4resume(returning: ()) }
            } // Apple’s API for one-time precise. :contentReference[oaicite:3]{index=3}
        }

        guard let user = CLLocationManager().location else {
            // In Simulator: set one via Features → Location → (Apple / Custom Location…)
            log = "❌ no location fix (Simulator: set Features → Location)"
            return
        }

        let μ = 1_000_000.0
        let userLat = Int64((user.coordinate.latitude  * μ).rounded())
        let userLon = Int64((user.coordinate.longitude * μ).rounded())
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
        else { log = "❌ missing ACIR/SRS in bundle"; return }

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
            log = "✅ proof bytes: \(proof.count) • verified: \(ok)"
        } catch {
            log = "❌ \(error)"
        }
    }
}
