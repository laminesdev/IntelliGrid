import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'IntelliGrid',
  description: 'Smart Home Energy Management System',
  icons: {
     icon: '/favicon.png',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-black text-white min-h-screen custom-scrollbar">
        {children}
      </body>
    </html>
  )
}
