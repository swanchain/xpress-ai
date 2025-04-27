// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract XpressPayment2 {
    AggregatorV3Interface internal dataFeed;
    address admin;
    mapping(string => uint) public uuidToCredits;
    event TweetsPurchased(address indexed payer, string indexed id, string uuid, uint numberOfTweets, uint price, uint paidAmount);

    constructor(address initialAdmin) {
        admin = initialAdmin;
        dataFeed = AggregatorV3Interface(
            0x2514895c72f50D8bd4B4F9b1110F0D6bD2c97526
        );
    }

    function getTotalCredits(string memory uuid) external view returns(uint) {
        return uuidToCredits[uuid];
    }
    
    function purchaseTweets(string memory uuid, uint numberOfTweets) external payable {
        uint price = getCreditPrice(numberOfTweets);
        require(msg.value >= price);

        uuidToCredits[uuid] += numberOfTweets;

        emit TweetsPurchased(msg.sender, uuid, uuid, numberOfTweets, price, msg.value);
    }

    function withdraw() public {
        require(msg.sender == admin, 'caller is not admin');
        address payable to = payable(msg.sender);
        to.transfer(address(this).balance);
    }

    /**
     * @notice get the latest USD price for 1 BNB (note the decimals)
     */
    function getLatestPrice() public view returns (int) {
        (
            /* uint80 roundId */,
            int256 answer,
            /*uint256 startedAt*/,
            /*uint256 updatedAt*/,
            /*uint80 answeredInRound*/
        ) = dataFeed.latestRoundData();
        return answer;
    }

    function getCreditPrice(uint numCredits) public view returns (uint) {
        int256 answer = getLatestPrice();
        uint creditPrice = 0.1 ether * numCredits * 10**8 / uint(answer);
        return creditPrice;
    }
}
