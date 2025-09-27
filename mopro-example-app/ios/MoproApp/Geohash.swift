import CoreLocation

enum Geohash {
    private static let base32 = Array("0123456789bcdefghjkmnpqrstuvwxyz")
    static func encode(lat: Double, lon: Double, precision: Int = 7) -> String {
        var latInt = (-90.0, 90.0)
        var lonInt = (-180.0, 180.0)
        var hash = ""
        var bit = 0, ch = 0
        var even = true
        while hash.count < precision {
            if even {
                let mid = (lonInt.0 + lonInt.1) / 2
                if lon > mid { ch |= 1 << (4 - bit); lonInt.0 = mid } else { lonInt.1 = mid }
            } else {
                let mid = (latInt.0 + latInt.1) / 2
                if lat > mid { ch |= 1 << (4 - bit); latInt.0 = mid } else { latInt.1 = mid }
            }
            even.toggle()
            if bit < 4 { bit += 1 } else { hash.append(base32[ch]); bit = 0; ch = 0 }
        }
        return hash
    }
}
