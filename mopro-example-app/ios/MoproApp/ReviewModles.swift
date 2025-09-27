import CoreLocation
import Foundation

struct ReviewPayload: Codable {
    var addr: String? = nil
    var signature: String? = nil
    var proofHex: String  // proof as hex string
    var publicInputsHex: String  // public inputs as hex string
    var geohash7: String  // computed from target
    var review: UserReview
    var expiresAt: UInt64  // now + 10 minutes (demo)
}

struct UserReview: Codable {
    var categories: [String]  // e.g. ["residential","green"]
    var rating: Int  // 1...5
    var text: String  // <= 280 chars
}

struct ReviewsResponse: Codable {
    var reviews: [ReviewRow]
}

struct ReviewRow: Codable, Identifiable {
    var id: String { "\(addr)-\(geohash7)-\(timestamp)" }
    var addr: String
    var geohash7: String
    var categories: [String]
    var rating: Int
    var text: String
    var timestamp: Int
    var proofHex: String?
    var publicInputsHex: String?
    var expiresAt: UInt64?
    var signature: String?

    enum CodingKeys: String, CodingKey {
        case addr, geohash7, categories, rating, text, timestamp, proofHex, publicInputsHex,
            expiresAt, signature
    }
}
