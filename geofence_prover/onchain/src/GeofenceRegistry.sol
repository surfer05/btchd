// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IVerifier {
    function verify(bytes calldata proof, bytes calldata publicInputs) external view returns (bool);
}

contract GeofenceRegistry {
    event ProofSubmitted(
        address indexed prover,
        bytes32 indexed geohash,   // geohash-7 of target
        int64 targetLat,           // micro-degrees
        int64 targetLon,           // micro-degrees
        int64 radiusMeters,
        uint256 submittedAt
    );

    IVerifier public immutable verifier;
    mapping(bytes32 => uint256) public lastUseByProofHash; // optional replay guard

    constructor(address _verifier) { verifier = IVerifier(_verifier); }

    // publicInputs encoding: abi.encode(int64 targetLat, int64 targetLon, int64 radiusMeters)
    function submit(bytes calldata proof, bytes calldata publicInputs, bytes32 geohashCell) external {
        require(verifier.verify(proof, publicInputs), "verify failed");

        // cheap replay guard: bind to this publicInputs hash
        bytes32 h = keccak256(publicInputs);
        require(lastUseByProofHash[h] == 0, "already used");
        lastUseByProofHash[h] = block.timestamp;

        (int64 lat, int64 lon, int64 radius) = abi.decode(publicInputs, (int64,int64,int64));
        emit ProofSubmitted(msg.sender, geohashCell, lat, lon, radius, block.timestamp);
    }
}
