import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import ContextProvider from '@/context'
import { headers } from 'next/headers' // added
import Head from 'next/head'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata = {
  title: 'XpressAI',
  description: 'Twitter Assistant',
  icons: {
    icon: '/chat-bot.png',
  },
}

export default async function RootLayout({ children }) {
  const headersData = await headers()
  const cookies = headersData.get('cookie')

  return (
    <html lang="en">
      <Head>
        <link
          href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </Head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ContextProvider cookies={cookies}>
          {/* <Navbar /> */}
          {children}
        </ContextProvider>
      </body>
    </html>
  )
}
