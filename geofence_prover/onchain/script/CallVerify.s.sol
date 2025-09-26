// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Script.sol";
import "../Verifier.sol";

contract CallVerify is Script {
    function run(address verifier) external {
        bytes memory proof = vm.parseBytes(vm.envString("PROOF_HEX")); // 0x...
        bytes32;
        inputs[0] = vm.parseBytes32(vm.envString("PUB0_HEX")); // target_lat
        inputs[1] = vm.parseBytes32(vm.envString("PUB1_HEX")); // target_lon
        inputs[2] = vm.parseBytes32(vm.envString("PUB2_HEX")); // radius
        vm.startBroadcast();
        bool ok = Verifier(verifier).verify(proof, inputs);
        console2.log("verify:", ok);
        vm.stopBroadcast();
    }
}
