import Link from "next/link"

const products = [
  {
    id: "orchestrator",
    name: "Productivity Orchestrator",
    tagline: "Your AI-powered personal project manager",
    description:
      "An always-on AI that observes your workflows, schedules tasks, drafts communications, summarizes meetings, and proactively manages your projects — 24/7.",
    features: [
      "Autonomous task scheduling & prioritization",
      "Smart meeting summaries",
      "Proactive research on your projects",
      "Multi-platform workflow integration",
    ],
    price: "$29",
    tier: "Pro",
    color: "from-violet-600 to-indigo-600",
    accent: "violet",
  },
  {
    id: "curator",
    name: "Intelli-Curator",
    tagline: "Hyper-personalized knowledge engine",
    description:
      "Continuously scans the web and academic databases to deliver a curated stream of news, learning paths, and research summaries tailored to your goals.",
    features: [
      "AI-curated news & research feed",
      "Personalized learning paths",
      "Deep-dive topic summaries",
      "Knowledge base that evolves with you",
    ],
    price: "$19",
    tier: "Pro",
    color: "from-emerald-600 to-teal-600",
    accent: "emerald",
  },
  {
    id: "guardian",
    name: "Digital Guardian",
    tagline: "Proactive AI security & privacy manager",
    description:
      "AI-powered security monitoring that detects threats, audits your digital footprint, and takes proactive steps to protect your privacy — before problems arise.",
    features: [
      "Real-time threat detection",
      "Privacy audit & recommendations",
      "Automated security responses",
      "Continuous digital footprint monitoring",
    ],
    price: "$24",
    tier: "Pro",
    color: "from-rose-600 to-pink-600",
    accent: "rose",
  },
]

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-950 text-white">
      {/* Hero */}
      <section className="py-24 px-6 text-center max-w-4xl mx-auto">
        <div className="inline-block bg-white/10 text-sm px-4 py-1 rounded-full mb-6 text-gray-300">
          AI-Powered Productivity Suite
        </div>
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Three AIs. One Goal.
          <br />
          Maximum Output.
        </h1>
        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Stop managing tools. Start accomplishing goals. Our three AI agents work autonomously
          so you focus on what matters.
        </p>
        <a
          href="#pricing"
          className="inline-block bg-white text-gray-950 font-semibold px-8 py-3 rounded-full hover:bg-gray-200 transition"
        >
          Get Started
        </a>
      </section>

      {/* Products */}
      <section id="pricing" className="py-16 px-6 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-4">Choose Your AI</h2>
        <p className="text-gray-400 text-center mb-12">
          Each tool is a standalone subscription. Get one or bundle all three.
        </p>

        <div className="grid md:grid-cols-3 gap-8">
          {products.map((p) => (
            <div
              key={p.id}
              className="bg-gray-900 border border-gray-800 rounded-2xl p-8 flex flex-col hover:border-gray-600 transition"
            >
              <div className={`inline-block bg-gradient-to-r ${p.color} text-white text-xs font-bold px-3 py-1 rounded-full mb-4 self-start`}>
                {p.tier}
              </div>
              <h3 className="text-xl font-bold mb-2">{p.name}</h3>
              <p className="text-gray-400 text-sm mb-4">{p.tagline}</p>
              <p className="text-gray-300 text-sm mb-6">{p.description}</p>
              <ul className="space-y-2 mb-8 flex-1">
                {p.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                    <span className="text-green-400 mt-0.5">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <div className="mt-auto">
                <div className="text-3xl font-bold mb-1">
                  {p.price}
                  <span className="text-gray-400 text-base font-normal">/mo</span>
                </div>
                <form action="/api/checkout" method="POST">
                  <input type="hidden" name="product" value={p.id} />
                  <button
                    type="submit"
                    className={`w-full mt-4 bg-gradient-to-r ${p.color} text-white font-semibold py-3 rounded-xl hover:opacity-90 transition`}
                  >
                    Subscribe Now
                  </button>
                </form>
              </div>
            </div>
          ))}
        </div>

        {/* Bundle */}
        <div className="mt-10 bg-gradient-to-r from-gray-800 to-gray-900 border border-gray-700 rounded-2xl p-8 text-center">
          <div className="inline-block bg-yellow-500 text-gray-950 text-xs font-bold px-3 py-1 rounded-full mb-4">
            BEST VALUE
          </div>
          <h3 className="text-2xl font-bold mb-2">Full Suite Bundle</h3>
          <p className="text-gray-400 mb-6">
            All three AI agents. One subscription. Save $12/mo vs individual plans.
          </p>
          <div className="text-4xl font-bold mb-6">
            $60<span className="text-gray-400 text-xl font-normal">/mo</span>{" "}
            <span className="text-gray-500 line-through text-xl">$72</span>
          </div>
          <form action="/api/checkout" method="POST">
            <input type="hidden" name="product" value="bundle" />
            <button
              type="submit"
              className="bg-yellow-500 text-gray-950 font-bold px-10 py-3 rounded-full hover:bg-yellow-400 transition"
            >
              Get Full Suite
            </button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 text-center text-gray-600 text-sm">
        <p>© 2026 AI Productivity Suite. All rights reserved.</p>
      </footer>
    </main>
  )
}
