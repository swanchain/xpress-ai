'use client'

import { useRouter } from 'next/navigation'
import Navbar from '../components/Navbar'
import { useAppKitAccount, useAppKit } from '@reown/appkit/react'
import LandingPage from '@/components/LandingPage'

export default function Home() {
  const { isConnected } = useAppKitAccount()
  const { open } = useAppKit()
  const router = useRouter()

  return (
    <>
      <Navbar />
      <LandingPage />
    </>
  )
}
