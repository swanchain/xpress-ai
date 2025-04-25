'use client'
import CloseIcon from '@/components/CloseIcon'
import LandingPage from '@/components/LandingPage'
import Navbar from '@/components/Navbar'
import TweetPage from '@/components/TweetPage'
import TwitterIcon from '@/components/TwitterIcon'
import useConnectX from '@/hooks/useConnectX'
import apiClient from '@/services/apiClient'
import { useAppKitAccount, useAppKitProvider } from '@reown/appkit/react'
import Head from 'next/head'
import { useEffect, useState } from 'react'
import { Contract, BrowserProvider, JsonRpcProvider } from 'ethers'
import CONTRACT_ABI from '@/abi/XpressPayment.json'

export default function Home() {
  const { isConnected, address } = useAppKitAccount()
  const { walletProvider } = useAppKitProvider('eip155')
  const { connectX, verifyXConnection, connectLoad } = useConnectX()
  const [user, setUser] = useState(null)
  const [selectedTab, setSelectedTab] = useState('create')
  const [showModal, setShowModal] = useState(false)
  const [purchaseLoading, setPurchaseLoading] = useState(false)
  const [transactionHash, setTransactionHash] = useState(null)
  const [availableCredits, setAvailableCredits] = useState(null)

  const CONTRACT_ADDRESS = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS
  const RPC_URL = process.env.NEXT_PUBLIC_RPC_URL
  const BLOCK_EXPLORER = process.env.NEXT_PUBLIC_BLOCK_EXPLORER

  useEffect(() => {
    verifyXConnection() // Automatically verifies connection if redirected from X
  }, [])

  const getUser = async () => {
    const token = localStorage.getItem('xpress_access_token')
    if (token) {
      const response = await apiClient.get('/user/get-user')
      // console.log(response.data.user)
      setUser(response.data.user)
    }
  }

  useEffect(() => {
    getUser()
  }, [connectLoad, transactionHash])

  useEffect(() => {
    const getCredits = async () => {
      const ethersProvider = new JsonRpcProvider(RPC_URL)
      const contract = new Contract(
        CONTRACT_ADDRESS,
        CONTRACT_ABI,
        ethersProvider,
      )

      const totalCredits = await contract.getTotalCredits(user.uuid)
      setAvailableCredits(Number(totalCredits) + 5 - user.total_generated)
    }

    if (user) {
      getCredits()
    }
  }, [user])

  const handlePurchase = async (numTweets) => {
    setTransactionHash('')
    setShowModal(false)
    setPurchaseLoading(true)

    try {
      const ethersProvider = new BrowserProvider(walletProvider)
      const signer = await ethersProvider.getSigner()
      const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer)

      const price = await contract.getCreditPrice(numTweets)

      const data = await contract.purchaseTweets(user.uuid, numTweets, {
        value: price,
      })
      // console.log('data: ', data)
      await data.wait()
      setTransactionHash(data.hash)
    } catch (err) {
      console.log('err', err)
      setPurchaseLoading(false)
      setShowModal(true)
    }

    // setPurchaseLoading(false)
  }

  return (
    <>
      <Head>
        <title>TweetAI Assistant</title>
        <link
          href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </Head>
      <div className="fixed -top-50 -right-25 w-[500px] h-[500px] rounded-full  bg-gradient-to-br from-[#84fab0] to-[#8fd3f4] z-10 blur-[100px] opacity-15" />
      <div className="fixed -bottom-50 -left-25 w-[500px] h-[500px] rounded-full  bg-gradient-to-br from-[#f6d365] to-[#fda085] z-10 blur-[100px] opacity-15" />
      <div className="relative min-h-screen bg-[#f5f5f7] text-dark font-display flex flex-col">
        {/* Navbar */}
        <Navbar
          user={user}
          setUser={setUser}
          selectedTab={selectedTab}
          setSelectedTab={setSelectedTab}
          setShowModal={setShowModal}
          availableCredits={availableCredits}
        />

        {/* Main Content */}
        <main className="flex-grow flex flex-col items-center justify-center px-4 text-center gap-5 z-30">
          {user ? (
            <TweetPage
              selectedTab={selectedTab}
              availableCredits={availableCredits}
              getUser={getUser}
            />
          ) : (
            <LandingPage />
          )}
        </main>
      </div>
      {/* purchase modal */}(
      <div
        className={`fixed inset-0 bg-black/50 flex items-start justify-center z-90 ${
          showModal
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setShowModal(false)}
      >
        <div
          className={` mt-10 bg-[#f2f2f2] rounded-[20px] p-4 transition-all duration-300 ease-out tranform ${
            showModal
              ? 'translate-y-0 opacity-100'
              : '-translate-y-10 opacity-0'
          }`}
          onClick={(e) => {
            e.stopPropagation() // Prevent click from bubbling to outer div
          }}
        >
          <div className="flex items-center mb-8 min-w-full gap-10">
            <h2 className="text-xl font-semibold justify-between w-full">
              Purchase Credits
            </h2>
            <div className="flex flex-row justify-center items-center gap-4">
              <div className="bg-black rounded-full">
                <w3m-button />
              </div>
              <div
                className="hover:cursor-pointer"
                onClick={() => setShowModal(false)}
              >
                <CloseIcon />
              </div>
            </div>
          </div>

          <div className="flex flex-row gap-6 mb-6 justify-evenly">
            <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200 ">
              <h2 className="font-semibold text-xl">Free</h2>
              <p className="lead font-semibold text-base">5 Tweets</p>
              <p className="m-2 mb-4">$0.00</p>
              <button
                onClick={() => handlePurchase(10)}
                disabled={true}
                className="black-btn text-base"
              >
                Purchase
              </button>
            </div>

            {/* <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200">
              <h2 className="font-semibold text-xl">Popular</h2>
              <p className="lead font-semibold text-base">20 Tweets</p>
              <p className="m-2 mb-4">$2.00</p>
              <button
                onClick={() => handlePurchase(20)}
                disabled={!isConnected}
                className="black-btn text-base"
              >
                Purchase
              </button>
            </div> */}

            <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200">
              <h2 className="font-semibold text-xl">Pro</h2>
              <p className="lead font-semibold text-base">10 Tweets</p>
              <p className="m-2 mb-4">$1.00</p>
              <button
                onClick={() => handlePurchase(10)}
                disabled={!isConnected}
                className="black-btn text-base"
              >
                Purchase
              </button>
            </div>

            {/* <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200">
              <h2 className="font-semibold text-xl">Enterprise</h2>
              <p className="lead font-semibold text-base">40 Tweets</p>
              <p className="m-2 mb-4">$4.00</p>
              <button
                onClick={() => handlePurchase(40)}
                disabled={!isConnected}
                className="black-btn text-base"
              >
                Purchase
              </button>
            </div> */}
          </div>
        </div>
      </div>
      ){/* tx modal */}
      <div
        className={`fixed inset-0 bg-black/50 flex items-start justify-center z-90 ${
          purchaseLoading
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none'
        }`}
      >
        <div
          className={`mt-20   bg-[#f2f2f2] rounded-[20px] p-4 transition-all duration-300 ease-out tranform ${
            purchaseLoading
              ? 'translate-y-0 opacity-100'
              : '-translate-y-40 opacity-0'
          }`}
          onClick={(e) => {
            e.stopPropagation() // Prevent click from bubbling to outer div
          }}
        >
          {transactionHash ? (
            <>
              <div className="flex flex-row items-center gap-2 mb-4">
                <svg
                  className="h-12 w-12 text-green-500"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10.293 15.293a1 1 0 011.414 0l5.5-5.5a1 1 0 10-1.414-1.414L11 13.586l-2.793-2.793a1 1 0 00-1.414 1.414l4 4z"
                    clipRule="evenodd"
                  />
                </svg>
                <h2 className="text-xl font-semibold text-gray-800">
                  Payment Successful!
                </h2>
              </div>
              <p className=" text-gray-600">
                Your transaction has been confirmed.
              </p>
              <a
                href={`${BLOCK_EXPLORER}/tx/${transactionHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className=" text-blue-600 hover:underline break-all text-center"
              >
                View on Explorer:{' '}
                <span className="">
                  {transactionHash.slice(0, 8)}...{transactionHash.slice(-6)}
                </span>
              </a>

              <div className="mt-8 w-full flex">
                <button
                  className="black-btn w-full bg-[#76b291] "
                  onClick={() => {
                    setPurchaseLoading(false)
                    setTransactionHash('')
                  }}
                >
                  Start Tweeting
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="flex flex-row items-center gap-2 mb-4">
                <svg
                  className="animate-spin h-8 w-8 text-blue-600"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                  />
                </svg>
                <h2 className="text-xl font-semibold ">
                  Processing Payment...
                </h2>
              </div>
              <p className=" text-gray-500">
                Please wait while your transaction is being confirmed.
              </p>
            </>
          )}
        </div>
      </div>
    </>
  )
}
