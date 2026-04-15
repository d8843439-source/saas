"use client"

import { useEffect, useState, useRef } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Suspense } from "react"

interface AnalysisItem {
  name: string
  dealerPrice: number
  fairPrice: number
  markupPct: number
  keep: boolean
  explanation: string
  script: string
}

interface Analysis {
  items: AnalysisItem[]
  totalDealerPrice: number
  totalFairPrice: number
  potentialSavings: number
  topTip: string
  error?: string
}

type State =
  | { status: "verifying" }
  | { status: "analyzing" }
  | { status: "done"; data: Analysis }
  | { status: "error"; message: string }

function ResultsContent() {
  const params = useSearchParams()
  const router = useRouter()
  const sessionId = params.get("session_id")
  const [state, setState] = useState<State>({ status: "verifying" })
  const ran = useRef(false)

  useEffect(() => {
    if (ran.current) return
    ran.current = true

    if (!sessionId) { router.replace("/analyze"); return }

    ;(async () => {
      // 1. Verify payment
      const vRes = await fetch(`/api/verify?session_id=${sessionId}`)
      const { verified } = await vRes.json()
      if (!verified) {
        setState({ status: "error", message: "Payment not confirmed. If you completed checkout, please wait a moment and refresh." })
        return
      }

      // 2. Get image from localStorage
      const image = localStorage.getItem("fs_image")
      if (!image) {
        setState({ status: "error", message: "Image not found — your browser may have cleared local storage. Please contact support for a refund or re-upload." })
        return
      }

      setState({ status: "analyzing" })

      // 3. Run analysis
      const aRes = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image }),
      })
      const data: Analysis = await aRes.json()

      if (data.error === "not_a_finance_menu") {
        setState({ status: "error", message: "We couldn't identify a dealership finance menu in your image. Please try again with a clearer photo of the add-on sheet." })
        return
      }
      if (data.error) {
        setState({ status: "error", message: `Analysis failed: ${data.error}. Please try again.` })
        return
      }

      // Clean up stored image
      localStorage.removeItem("fs_image")
      setState({ status: "done", data })
    })()
  }, [sessionId, router])

  if (state.status === "verifying") return <LoadingScreen message="Verifying your payment…" />
  if (state.status === "analyzing") return <LoadingScreen message="Analyzing your finance menu…" sub="This takes about 10 seconds" />
  if (state.status === "error") return <ErrorScreen message={state.message} />

  const { data } = state
  const skipItems = data.items.filter((i) => !i.keep)
  const keepItems = data.items.filter((i) => i.keep)

  return (
    <main className="min-h-screen bg-[#080808] text-white pb-20">
      <nav className="max-w-3xl mx-auto px-6 py-5 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg tracking-tight">FinalOffer</Link>
        <span className="text-gray-500 text-sm">Your Report</span>
      </nav>

      <div className="max-w-3xl mx-auto px-6">

        {/* Savings summary */}
        <div className="bg-gradient-to-br from-green-950/60 to-[#0f0f0f] border border-green-500/20 rounded-2xl p-8 mb-8 text-center">
          <p className="text-gray-400 text-sm uppercase tracking-widest mb-2">Potential savings found</p>
          <p className="text-6xl font-bold text-green-400 mb-2">${data.potentialSavings.toLocaleString()}</p>
          <p className="text-gray-400 text-sm">
            Dealer total: <span className="line-through text-gray-500">${data.totalDealerPrice.toLocaleString()}</span>
            {" · "}Fair value: <span className="text-white">${data.totalFairPrice.toLocaleString()}</span>
          </p>
        </div>

        {/* Top tip */}
        {data.topTip && (
          <div className="bg-amber-400/10 border border-amber-400/20 rounded-xl p-4 mb-8">
            <p className="text-xs text-amber-400 font-semibold uppercase tracking-widest mb-1">Pro tip</p>
            <p className="text-gray-300 text-sm">{data.topTip}</p>
          </div>
        )}

        {/* Items to skip */}
        {skipItems.length > 0 && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-red-400 rounded-full" />
              Decline these ({skipItems.length})
            </h2>
            <div className="space-y-4">
              {skipItems.map((item) => (
                <ItemCard key={item.name} item={item} />
              ))}
            </div>
          </section>
        )}

        {/* Items to keep */}
        {keepItems.length > 0 && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full" />
              These are worth keeping ({keepItems.length})
            </h2>
            <div className="space-y-4">
              {keepItems.map((item) => (
                <ItemCard key={item.name} item={item} />
              ))}
            </div>
          </section>
        )}

        {/* Share CTA */}
        <div className="bg-[#0f0f0f] border border-[#1e1e1e] rounded-2xl p-6 text-center">
          <p className="font-semibold mb-1">Screenshot and bring this to the dealership</p>
          <p className="text-gray-500 text-sm mb-4">Or share your savings on TikTok/Reels to help other buyers</p>
          <Link href="/analyze" className="text-amber-400 hover:text-amber-300 text-sm transition">
            Analyze another deal →
          </Link>
        </div>

      </div>
    </main>
  )
}

function ItemCard({ item }: { item: AnalysisItem }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-2xl overflow-hidden">
      <div
        className="p-5 flex items-start justify-between gap-4 cursor-pointer"
        onClick={() => setOpen((o) => !o)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-semibold">{item.name}</span>
            {item.keep ? (
              <span className="text-xs bg-green-500/15 text-green-400 px-2 py-0.5 rounded-full">KEEP</span>
            ) : (
              <span className="text-xs bg-red-500/15 text-red-400 px-2 py-0.5 rounded-full">SKIP</span>
            )}
          </div>
          <p className="text-gray-500 text-xs">{item.explanation}</p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-gray-500 line-through text-sm">${item.dealerPrice.toLocaleString()}</p>
          <p className={`font-bold text-sm ${item.keep ? "text-gray-300" : "text-green-400"}`}>
            {item.keep
              ? `Fair: $${item.fairPrice.toLocaleString()}`
              : `Save $${(item.dealerPrice - item.fairPrice).toLocaleString()}`}
          </p>
          <p className="text-gray-700 text-xs">{open ? "▲" : "▼"}</p>
        </div>
      </div>

      {open && (
        <div className="border-t border-[#1a1a1a] p-5 bg-[#0a0a0a]">
          <p className="text-xs text-amber-400 font-semibold uppercase tracking-widest mb-2">
            {item.keep ? "Why it's worth keeping" : "What to say"}
          </p>
          {!item.keep && (
            <div className="bg-[#111] border border-[#222] rounded-xl p-4 mb-3">
              <p className="text-gray-200 text-sm italic">"{item.script}"</p>
            </div>
          )}
          {item.fairPrice > 0 && !item.keep && (
            <p className="text-gray-500 text-xs">
              Fair market price: ~${item.fairPrice.toLocaleString()} (through your insurer or third party)
            </p>
          )}
          {item.keep && (
            <p className="text-gray-400 text-sm">{item.explanation}</p>
          )}
        </div>
      )}
    </div>
  )
}

function LoadingScreen({ message, sub }: { message: string; sub?: string }) {
  return (
    <div className="min-h-screen bg-[#080808] flex flex-col items-center justify-center gap-4">
      <div className="w-10 h-10 border-2 border-amber-400/30 border-t-amber-400 rounded-full animate-spin" />
      <p className="text-white font-semibold">{message}</p>
      {sub && <p className="text-gray-500 text-sm">{sub}</p>}
    </div>
  )
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <div className="min-h-screen bg-[#080808] flex flex-col items-center justify-center px-6 text-center gap-6">
      <p className="text-4xl">⚠️</p>
      <p className="text-white font-semibold text-lg max-w-md">{message}</p>
      <Link href="/analyze" className="bg-amber-400 hover:bg-amber-300 text-black font-bold px-6 py-3 rounded-xl transition">
        Try Again
      </Link>
    </div>
  )
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<LoadingScreen message="Loading…" />}>
      <ResultsContent />
    </Suspense>
  )
}
