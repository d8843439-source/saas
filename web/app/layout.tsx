import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "AI Productivity Suite",
  description: "Three powerful AI tools to maximize your productivity, knowledge, and digital security.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-white">{children}</body>
    </html>
  )
}
