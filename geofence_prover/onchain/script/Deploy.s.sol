// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Script.sol";
import "../Verifier.sol";

contract Deploy is Script {
    function run() external {
        vm.startBroadcast();
        Verifier v = new Verifier();
        console2.log("Verifier:", address(v));
        vm.stopBroadcast();
    }
}
