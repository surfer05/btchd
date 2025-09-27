import CoreLocation
import Foundation

enum ReviewAPI {
    static var baseURL = URL(
        string: "https://super-duper-space-waffle-xx49jw799gw3pg7g-5000.app.github.dev")!  // change to your LAN IP on device

    static func submit(
        target: CLLocationCoordinate2D,
        categories: [String], rating: Int, text: String,
        proof: Data?, publicInputs: Data?
    ) async throws {
        let gh = Geohash.encode(lat: target.latitude, lon: target.longitude, precision: 7)
        let expires: UInt64 = UInt64(Date().addingTimeInterval(10 * 60).timeIntervalSince1970)

        // Convert proof and public inputs to hex strings
        let proofHex = proof?.map { String(format: "%02x", $0) }.joined(separator: "") ?? "0x"
        let publicInputsHex =
            publicInputs?.map { String(format: "%02x", $0) }.joined(separator: "") ?? "0x"

        let payload = ReviewPayload(
            proofHex: proofHex,
            publicInputsHex: publicInputsHex,
            geohash7: gh,
            review: .init(categories: categories, rating: rating, text: text),
            expiresAt: expires)

        var req: URLRequest = URLRequest(url: baseURL.appendingPathComponent("/submit"))
        req.httpMethod = "POST"
        req.addValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONEncoder().encode(payload)

        _ = try await URLSession.shared.data(for: req)  // throws on non-2xx; returns (data,response)
    }

    static func fetch(prefix: String?) async throws -> [ReviewRow] {
        var url = baseURL.appendingPathComponent("/reviews")
        if let prefix, let comp = URLComponents(string: url.absoluteString) {
            var u = comp
            u.queryItems = [URLQueryItem(name: "prefix", value: prefix)]
            if let built = u.url { url = built }
        }
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(ReviewsResponse.self, from: data).reviews
    }
}
