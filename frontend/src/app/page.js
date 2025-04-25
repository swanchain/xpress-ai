'use client'
import CloseIcon from '@/components/CloseIcon'
import LandingPage from '@/components/LandingPage'
import Navbar from '@/components/Navbar'
import TweetPage from '@/components/TweetPage'
import TwitterIcon from '@/components/TwitterIcon'
import useConnectX from '@/hooks/useConnectX'
import apiClient from '@/services/apiClient'
import Head from 'next/head'
import { useEffect, useState } from 'react'

export default function Home() {
  const { connectX, verifyXConnection, connectLoad } = useConnectX()
  const [user, setUser] = useState(null)
  const [selectedTab, setSelectedTab] = useState('create')
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    verifyXConnection() // Automatically verifies connection if redirected from X
  }, [])

  useEffect(() => {
    const getUser = async () => {
      const response = await apiClient.get('/user/get-user')
      console.log(response.data.user)
      setUser(response.data.user)
    }
    const token = localStorage.getItem('xpress_access_token')

    if (token) {
      getUser()
    }
  }, [connectLoad])

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
        />

        {/* Main Content */}
        <main className="flex-grow flex flex-col items-center justify-center px-4 text-center gap-5 z-30">
          {user ? <TweetPage selectedTab={selectedTab} /> : <LandingPage />}
        </main>
      </div>
      (
      <div
        className={`fixed inset-0 bg-black/50 flex items-start justify-center z-90 ${
          showModal
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setShowModal(false)}
      >
        <div
          className={`mt-10 bg-[#f2f2f2] rounded-[20px] p-4 transition-all duration-300 ease-out tranform ${
            showModal
              ? 'translate-y-0 opacity-100'
              : '-translate-y-10 opacity-0'
          }`}
          onClick={(e) => {
            e.stopPropagation() // Prevent click from bubbling to outer div
          }}
        >
          <div className="flex items-center mb-8">
            <h2 className="text-xl font-semibold justify-between w-full">
              Purchase Credits
            </h2>
            <div
              className="hover:cursor-pointer"
              onClick={() => setShowModal(false)}
            >
              <CloseIcon />
            </div>
          </div>
          <div className="flex flex-row gap-6 mb-6">
            <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200">
              <h2 className="font-semibold text-xl">Starter</h2>
              <p className="lead font-semibold text-base">10 Tweets</p>
              <p className="m-2 mb-4">$1.00</p>
              <button className="black-btn text-base">Purchase</button>
            </div>

            <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200">
              <h2 className="font-semibold text-xl">Popular</h2>
              <p className="lead font-semibold text-base">20 Tweets</p>
              <p className="m-2 mb-4">$2.00</p>
              <button className="black-btn text-base">Purchase</button>
            </div>

            <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200">
              <h2 className="font-semibold text-xl">Pro</h2>
              <p className="lead font-semibold text-base">30 Tweets</p>
              <p className="m-2 mb-4">$3.00</p>
              <button className="black-btn text-base">Purchase</button>
            </div>

            <div className="flex flex-col justify-center items-center bg-white rounded-[20px] p-8 border-1 border-gray-200">
              <h2 className="font-semibold text-xl">Enterprise</h2>
              <p className="lead font-semibold text-base">40 Tweets</p>
              <p className="m-2 mb-4">$4.00</p>
              <button className="black-btn text-base">Purchase</button>
            </div>
          </div>
        </div>
      </div>
      )
    </>
  )
}
