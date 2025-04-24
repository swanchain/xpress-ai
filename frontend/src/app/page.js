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
  const [pageSelect, usePageSelect] = useState('tweet')

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
  }, [])

  return (
    <>
      <Head>
        <title>TweetAI Assistant</title>
        <link
          href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </Head>

      <div className="relative min-h-screen bg-[#f5f5f7] text-dark font-display flex flex-col">
        {/* Navbar */}
        <Navbar user={user} />

        {/* Main Content */}
        <main className="flex-grow flex flex-col items-center justify-center px-4 text-center gap-5 bg-">
          {user ? <TweetPage /> : <LandingPage />}
        </main>
      </div>
    </>
  )
}
