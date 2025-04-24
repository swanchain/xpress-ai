import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import ContextProvider from '@/context'
import { headers } from 'next/headers' // added

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata = {
  title: 'Xpress.ai',
  description: 'Xpress yourself',
}

export default async function RootLayout({ children }) {
  const headersData = await headers()
  const cookies = headersData.get('cookie')

  return (
    <html lang="en">
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
