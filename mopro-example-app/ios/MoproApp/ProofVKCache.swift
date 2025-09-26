import Foundation
//import MoproFFI

final class ProofVKCache {
    static let shared = ProofVKCache()
    private init() {}
    private var vkCache: Data?

    func getVK(circuitPath: String, srsPath: String, onChain: Bool, lowMem: Bool) throws -> Data {
        if let vk = vkCache { return vk }
        let vk = try getNoirVerificationKey(
            circuitPath: circuitPath,
            srsPath: srsPath,
            onChain: onChain,
            lowMemoryMode: lowMem
        )
        vkCache = vk
        return vk
    }
}
