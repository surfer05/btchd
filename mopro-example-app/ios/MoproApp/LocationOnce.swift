import CoreLocation

final class LocationOnce: NSObject, CLLocationManagerDelegate {
    private let mgr = CLLocationManager()
    private var cont: ((CLLocation) -> Void)?

    override init() {
        super.init()
        mgr.delegate = self
        mgr.desiredAccuracy = kCLLocationAccuracyBest
    }

    func request(_ cont: @escaping (CLLocation) -> Void) {
        self.cont = cont

        // Request when-in-use first.
        let status = mgr.authorizationStatus
        if status == .notDetermined {
            mgr.requestWhenInUseAuthorization()
        }

        // If approximate, ask for temporary full accuracy (purpose key must match Info.plist dictionary).
        if mgr.accuracyAuthorization == .reducedAccuracy {
            mgr.requestTemporaryFullAccuracyAuthorization(withPurposeKey: "GeofenceProof") { _ in
                self.mgr.requestLocation()
            }
        } else {
            mgr.requestLocation()
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        if let loc = locations.last { cont?(loc) }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location error:", error.localizedDescription)
    }
}
