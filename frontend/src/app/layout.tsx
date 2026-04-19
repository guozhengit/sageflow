import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/lib/theme'
import ErrorBoundary from '@/components/ui/ErrorBoundary'
import ToastContainer from '@/components/ui/Toast'
import GlobalLoading from '@/components/ui/GlobalLoading'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SageFlow - Smart Q&A Solutions',
  description: '智慧如流，洞察如光 - 智能问答解决方案',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <ErrorBoundary>
            {children}
            <ToastContainer />
            <GlobalLoading />
          </ErrorBoundary>
        </ThemeProvider>
      </body>
    </html>
  )
}
