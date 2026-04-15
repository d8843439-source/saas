import Link from "next/link"

export default function SuccessPage() {
  return (
    <main className="min-h-screen bg-[#080808] text-white flex items-center justify-center">
      <div className="text-center max-w-md px-6">
        <div className="text-6xl mb-6">&#x2705;</div>
        <h1 className="text-3xl font-bold mb-4">Payment received!</h1>
        <p className="text-gray-400 mb-8">
          Your FinalOffer report is being generated. You should be redirected automatically.
          If not, click below.
        </p>
        <Link
          href="/analyze"
          className="inline-block bg-amber-400 text-black font-bold px-8 py-3 rounded-xl hover:bg-amber-300 transition"
        >
          Back to Analyze
        </Link>
      </div>
    </main>
  )
}
