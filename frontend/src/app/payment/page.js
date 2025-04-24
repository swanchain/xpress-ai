'use client'
import { useState } from 'react'
import Head from 'next/head'
import { useAppKitAccount } from '@reown/appkit/react'
import Navbar from '@/components/Navbar'

export default function Payment() {
  const { isConnected, address, connect } = useAppKitAccount()
  const [tweetCount, setTweetCount] = useState(5)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const pricePerTweet = 0.01 // in ETH or appropriate token
  const totalPrice = tweetCount * pricePerTweet

  const handleSubmit = async () => {
    if (!isConnected) {
      connect()
      return
    }
    setIsSubmitting(true)

    try {
      // Replace this with your actual smart contract interaction logic
      console.log(
        `Calling contract with ${tweetCount} tweets for ${totalPrice} ETH by ${address}`,
      )
      // e.g. contract.methods.purchaseTweets(tweetCount).send({ from: address, value: web3.utils.toWei(totalPrice.toString(), 'ether') });

      alert('Transaction submitted successfully!')
    } catch (err) {
      console.error(err)
      alert('There was an error submitting the transaction.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <Head>
        <title>Purchase Tweets — Xpress.ai</title>
      </Head>
      <Navbar />
      <main className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <h2 className="text-2xl font-bold mb-4 text-center">
            Purchase Tweets
          </h2>

          <div className="mb-6">
            <label
              htmlFor="tweetCount"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Number of Tweets
            </label>
            <input
              type="number"
              id="tweetCount"
              value={tweetCount}
              min={1}
              onChange={(e) => setTweetCount(Number(e.target.value))}
              className="w-full p-3 border border-gray-300 rounded-lg"
            />
          </div>

          <div className="text-center mb-6">
            <p className="text-lg">
              Total: <strong>{totalPrice.toFixed(2)} ETH</strong>
            </p>
          </div>

          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="w-full bg-blue-600 text-white py-3 rounded-xl text-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {isConnected
              ? isSubmitting
                ? 'Submitting...'
                : 'Submit Payment'
              : 'Connect Wallet'}
          </button>
        </div>
      </main>
    </>
  )
}
