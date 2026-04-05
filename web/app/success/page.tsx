export default function SuccessPage() {
  return (
    <main className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="text-center max-w-md px-6">
        <div className="text-6xl mb-6">🎉</div>
        <h1 className="text-3xl font-bold mb-4">You&apos;re all set!</h1>
        <p className="text-gray-400 mb-8">
          Your subscription is active. Check your email for next steps and access instructions.
        </p>
        <a
          href="/"
          className="inline-block bg-white text-gray-950 font-semibold px-8 py-3 rounded-full hover:bg-gray-200 transition"
        >
          Back to Home
        </a>
      </div>
    </main>
  )
}
