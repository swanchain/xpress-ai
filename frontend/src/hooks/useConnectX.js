'use client'

import { useState } from 'react'
import apiClient from '@/services/apiClient'
import { useSearchParams, useRouter } from 'next/navigation'
import { toast } from 'react-toastify'
import axios from 'axios'

export default function useConnectX() {
  const [connectLoad, setConnectLoad] = useState(false)
  const searchParams = useSearchParams()
  const router = useRouter()

  const connectX = async () => {
    if (connectLoad) return

    setConnectLoad(true)

    try {
      // Step 1: Get OAuth Authorization URL
      const res = await apiClient.get(`user/x_oauth_login`)
      const authData = res.data

      if (authData?.data?.authorized_url) {
        window.location.href = authData.data.authorized_url
      }
    } catch (error) {
      toast.error(
        error?.response?.data?.detail ||
          error?.message ||
          'Error during OAuth login',
        {
          position: 'top-center',
          autoClose: 3000,
        },
      )
      console.error('Error during OAuth login:', error)
    } finally {
      setConnectLoad(false)
    }
  }

  const verifyXConnection = async () => {
    const formData = new FormData()
    const oauth_token = searchParams.get('oauth_token')
    const oauth_verifier = searchParams.get('oauth_verifier')

    if (!oauth_token || !oauth_verifier) return

    formData.append('oauth_token', oauth_token)
    formData.append('oauth_verifier', oauth_verifier)

    setConnectLoad(true)

    try {
      // Step 2: Send OAuth Token & Verifier to Backend
      const res = await apiClient.post(`user/login_x_account`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (res.status == 200) {
        localStorage.setItem('xpress_access_token', res.data.access_token)
        localStorage.setItem('xpress_username', res.data.user.x_screen_name)
      }

      console.log('X account successfully connected')
    } catch (error) {
      // Check if error response status is 400 (bad request)
      if (axios.isAxiosError(error) && error.response?.status === 400) {
        toast.error(
          error.response.data.detail ?? 'Error verifying X connection',
          {
            position: 'top-center',
            autoClose: 3000,
          },
        )
      } else {
        console.error('Error verifying X connection:', error)
      }
    } finally {
      //   router.push('/account?socials=true&') // Redirect after successful connection
      setConnectLoad(false)
    }
  }

  return { connectLoad, connectX, verifyXConnection }
}
