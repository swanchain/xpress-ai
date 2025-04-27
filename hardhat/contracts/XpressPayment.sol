// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

// Uncomment this line to use console.log
// import "hardhat/console.sol";
import { SignatureVerifierLib } from './SignatureVerifierLib.sol';

contract XpressPayment {
    address admin;
    mapping(uint => address) public idToUser;
    event TweetsPurchased(address indexed payer, uint indexed id, uint numberOfTweets, uint price);

    constructor(address initialAdmin) {
        admin = initialAdmin;
    }

    modifier verifySignature(
        uint _id,
        uint _numberOfTweets,
        uint _price,
        uint _expiry,
        bytes memory _signature) {
        require(block.timestamp < _expiry, 'signature is expired');
        require(msg.value == _price, 'user payment amount does not match the price');

        address signer = SignatureVerifierLib.recoverSigner(address(this), msg.sender, _id, _numberOfTweets, _price, _expiry, _signature);
        require(signer == admin, 'signature verification failed');
        _;
    }

    function isPaymentComplete(uint id) external view returns(bool) {
        return idToUser[id] != address(0);
    }
    
    function purchaseTweets(uint id, uint numberOfTweets, uint price, uint expiry, bytes memory signature) external payable verifySignature(id, numberOfTweets, price, expiry, signature) {
        emit TweetsPurchased(msg.sender, id, numberOfTweets, price);
    }

    function withdraw() public {
        require(msg.sender == admin, 'caller is not admin');
        address payable to = payable(msg.sender);
        to.transfer(address(this).balance);
    }
}
