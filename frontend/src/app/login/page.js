// app/login/page.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/services/apiClient'
import { toast } from 'react-toastify'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Email and password are required', { position: 'top-center' })
      return
    }

    setIsLoading(true)
    try {
      const { data } = await apiClient.post('/auth/login', { email, password })
      localStorage.setItem('access_token', data.access_token)
      toast.success('Login successful!', { position: 'top-center' })
      router.push('/admin/home')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed', {
        position: 'top-center',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white p-8 rounded-lg shadow">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold">Xpress.ai</h1>
          <p className="text-gray-500 text-sm mt-2"></p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="w-full mt-1 p-3 border rounded-lg focus:outline-none focus:ring"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="w-full mt-1 p-3 border rounded-lg focus:outline-none focus:ring"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 mt-4 font-medium text-white rounded-lg ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-black hover:bg-gray-800'
            }`}
          >
            {isLoading ? 'Logging in…' : 'Login'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/register')}
            className="w-full py-3 mt-2 font-medium bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Sign Up
          </button>
        </form>
      </div>
    </div>
  )
}
