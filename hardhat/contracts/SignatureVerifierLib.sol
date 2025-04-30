// // SPDX-License-Identifier: MIT
// pragma solidity ^0.8.0;

// import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
// import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

// /**
//  * @title 
//  * @notice This library is used to recover the address responsible for signing a given message.
//  * @dev From the signed info + the signature, we can recover the signer
//  */
// library SignatureVerifierLib {
//     using ECDSA for bytes32;
//     using MessageHashUtils for bytes32;

//     function recoverSigner(
//         address contractAddress,
//         address callerAddress,
//         uint id,
//         uint numTweets,
//         uint price,
//         uint expiry,
//         bytes memory signature
//     ) internal pure returns (address) {
//         bytes32 messageHash = keccak256(abi.encodePacked(contractAddress, callerAddress, id, numTweets, price, expiry));
//         bytes32 ethSignedMessageHash = messageHash.toEthSignedMessageHash();

//         return ethSignedMessageHash.recover(signature);
//     }
// }