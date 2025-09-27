// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import "forge-std/Script.sol";
import "../src/GeofenceRegistry.sol";

contract Deploy is Script {
    function run() external {
        address verifier = vm.envAddress("VERIFIER_ADDR"); // deployed Verifier.sol address
        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));
        GeofenceRegistry reg = new GeofenceRegistry(verifier);
        vm.stopBroadcast();
        console2.log("GeofenceRegistry:", address(reg));
    }
}
