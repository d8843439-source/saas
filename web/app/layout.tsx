import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "FinalOffer — Know Before You Sign",
  description: "Upload your dealer's finance menu. AI finds every overpriced add-on and gives you the exact words to say to remove it.",
  openGraph: {
    title: "FinalOffer — Know Before You Sign",
    description: "The average car buyer overpays $1,700 in the finance office. Not anymore.",
    type: "website",
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-[#080808] text-white antialiased">{children}</body>
    </html>
  )
}
