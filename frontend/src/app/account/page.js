// app/account/page.jsx
'use client'

import useConnectX from '@/hooks/useConnectX'
import { useAppKit } from '@reown/appkit/react'
import { useAppKitAccount } from '@reown/appkit/react'
import { useState } from 'react'

export default function AccountPage() {
  const { open } = useAppKit() // to open modals
  const { isConnected, address } = useAppKitAccount()
  const [amount, setAmount] = useState('')
  const { connectX, verifyXConnection, connectLoad } = useConnectX()

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Account Settings</h1>

      {/* 1) Social / X/Twitter login */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Social Login</h2>
        {!isConnected ? (
          <button
            onClick={connectX}
            className="px-5 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Connect X (Twitter)
          </button>
        ) : (
          <div className="text-green-600">Connected as {address}</div>
        )}

        <button
          onClick={connectX}
          className="px-5 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Connect X (Twitter)
        </button>
      </section>

      {/* 2) On-Ramp (Deposit) */}
      <section className="mb-8 max-w-sm">
        <h2 className="text-xl font-semibold mb-2">Deposit Funds</h2>
        <input
          type="text"
          placeholder="Tweet Credits"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="w-full px-3 py-2 border rounded mb-2"
        />
        <button
          onClick={() =>
            open({
              view: 'On-Ramp',
              defaultCurrency: 'ETH',
              defaultAmount: amount,
            })
          }
          className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          disabled={!amount}
        >
          Deposit
        </button>
      </section>
    </div>
  )
}
