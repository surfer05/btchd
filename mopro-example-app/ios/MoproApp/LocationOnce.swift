import CoreLocation

final class LocationOnce: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var completion: ((Result<CLLocation, CLError>) -> Void)?

    func requestResult(_ completion: @escaping (Result<CLLocation, CLError>) -> Void) {
        self.completion = completion
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.requestLocation()  // one-shot fix per Apple. :contentReference[oaicite:1]{index=1}
    }

    // Keep your existing convenience wrapper (optional, for backwards compatibility)
    func request(_ success: @escaping (CLLocation) -> Void) {
        requestResult { if case .success(let loc) = $0 { success(loc) } }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        if let loc = locations.last {
            completion?(.success(loc))
            completion = nil; manager.delegate = nil
        }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        if let e = error as? CLError {
            completion?(.failure(e))   // .denied, .locationUnknown, etc. :contentReference[oaicite:2]{index=2}
        } else {
            completion?(.failure(CLError(.locationUnknown)))
        }
        completion = nil; manager.delegate = nil
    }
}
