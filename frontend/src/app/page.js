'use client'
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
    </>
  )
}
