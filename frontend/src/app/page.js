'use client'

import { useRouter } from 'next/navigation'
import { Navbar } from '../components/NavBar'
import { useAppKitAccount, useAppKit } from '@reown/appkit/react'

export default function Home() {
  const { isConnected } = useAppKitAccount()
  const { open } = useAppKit()
  const router = useRouter()

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Hero */}
      <header className="flex-grow flex flex-col items-center justify-center text-center px-6">
        <h1 className="text-5xl md:text-6xl font-extrabold mb-4">Xpress.ai</h1>
        <p className="text-xl md:text-2xl text-gray-600 max-w-2xl mb-8">
          Unlock the power of AI-driven tweets—crafted in your unique voice,
          fueled by GPT-4o & DeepSeek.
        </p>
        {!isConnected && (
          <p className="text-sm text-red-500 mb-6">
            Connect your wallet to get started—no credit card required.
          </p>
        )}
        <button
          onClick={() => (isConnected ? router.push('/account') : open())}
          className="px-8 py-4 bg-blue-600 text-white rounded-lg text-lg hover:bg-blue-700 transition"
        >
          {isConnected ? 'Go to Dashboard' : 'Connect Wallet'}
        </button>
      </header>

      {/* Features */}
      <section className="py-16 px-6 md:px-0 max-w-5xl mx-auto grid gap-10 md:grid-cols-2">
        <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
          <h2 className="text-2xl font-semibold mb-2">
            Phase 1: Tweet Like You
          </h2>
          <p className="text-gray-700 mb-4">
            By analyzing your past tweets and trending topics, Xpress.ai crafts
            suggestions that match your style—so every tweet feels authentically
            you.
          </p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
          <h2 className="text-2xl font-semibold mb-2">
            Phase 2: Smart Replies
          </h2>
          <p className="text-gray-700 mb-4">
            Summarize threads, generate supportive, neutral, or debate-style
            replies, and flag risky content—timely, on-brand responses at your
            fingertips.
          </p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
          <h2 className="text-2xl font-semibold mb-2">
            Trend-Driven Engagement
          </h2>
          <p className="text-gray-700 mb-4">
            Spot viral tweets for retweets or quotes with compelling
            commentary—boost visibility and grow your audience effortlessly.
          </p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
          <h2 className="text-2xl font-semibold mb-2">
            Future: Omni-Channel Replies
          </h2>
          <p className="text-gray-700 mb-4">
            Coming soon—automate DMs and replies across X, Telegram, WhatsApp,
            Signal, Reachme.io, and more.
          </p>
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-white py-16 px-6 md:px-0">
        <div className="max-w-3xl mx-auto text-center mb-8">
          <h2 className="text-3xl font-bold">Pricing Plans</h2>
          <p className="text-gray-600">
            Start free, scale with Pro as you grow.
          </p>
        </div>
        <div className="max-w-4xl mx-auto grid gap-8 md:grid-cols-2">
          <div className="p-6 border rounded-xl">
            <h3 className="text-2xl font-semibold mb-2">Free Plan</h3>
            <p className="text-gray-700 mb-4">
              5 AI-powered tweet suggestions—test the magic at no cost.
            </p>
            <span className="text-4xl font-bold">Free</span>
          </div>
          <div className="p-6 border rounded-xl">
            <h3 className="text-2xl font-semibold mb-2">Pro Plan</h3>
            <p className="text-gray-700 mb-4">
              ₿0.015 (≈$0.10) per suggestion. Bulk packs unlock historical-data
              training and volume discounts.
            </p>
            <span className="text-4xl font-bold">₿0.015</span>
            <p className="text-sm text-gray-500 mt-1">per tweet suggestion</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 text-center text-gray-500 text-sm">
        © {new Date().getFullYear()} Xpress.ai • Crafted with AI for your voice.
      </footer>
    </div>
  )
}
