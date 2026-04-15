import Link from "next/link"

const SAMPLE_ITEMS = [
  { name: "GAP Insurance", dealer: 895, fair: 200, save: 695, skip: true },
  { name: "Extended Warranty (VSC)", dealer: 2400, fair: 0, save: 2400, skip: true },
  { name: "Paint & Fabric Protection", dealer: 599, fair: 0, save: 599, skip: true },
  { name: "Nitrogen in Tires", dealer: 249, fair: 0, save: 249, skip: true },
]

const TOTAL_SAVE = SAMPLE_ITEMS.reduce((s, i) => s + i.save, 0)

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#080808] text-white">

      {/* Nav */}
      <nav className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between">
        <span className="font-bold text-lg tracking-tight">FinalOffer</span>
        <Link href="/analyze" className="bg-amber-400 hover:bg-amber-300 text-black font-semibold px-4 py-2 rounded-lg text-sm transition">
          Analyze My Deal →
        </Link>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 pt-16 pb-20 text-center">
        <div className="inline-flex items-center gap-2 bg-amber-400/10 border border-amber-400/30 text-amber-400 text-sm px-4 py-1.5 rounded-full mb-8">
          <span className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
          The average buyer overpays $1,700 in the finance office
        </div>

        <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6 tracking-tight">
          Walk out of the dealership<br />
          <span className="text-amber-400">$2,000 richer.</span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Snap a photo of your dealer's finance menu. AI identifies every overpriced add-on
          and gives you the <span className="text-white font-medium">exact words to say</span> to remove it.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link href="/analyze" className="bg-amber-400 hover:bg-amber-300 text-black font-bold px-8 py-4 rounded-xl text-lg transition w-full sm:w-auto">
            Analyze My Deal — $19
          </Link>
          <span className="text-gray-500 text-sm">One-time. Instant results. No subscription.</span>
        </div>
      </section>

      {/* Sample Report */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <p className="text-center text-gray-500 text-sm uppercase tracking-widest mb-6">Sample Report</p>
        <div className="bg-[#0f0f0f] border border-[#1e1e1e] rounded-2xl overflow-hidden">
          <div className="border-b border-[#1e1e1e] p-6 flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">FinalOffer Analysis</p>
              <p className="font-semibold text-lg">Finance Office Add-Ons</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 mb-1">Potential savings</p>
              <p className="text-3xl font-bold text-green-400">${TOTAL_SAVE.toLocaleString()}</p>
            </div>
          </div>

          <div className="divide-y divide-[#1a1a1a]">
            {SAMPLE_ITEMS.map((item) => (
              <div key={item.name} className="px-6 py-4 flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-medium text-sm">{item.name}</span>
                    <span className="text-xs bg-red-500/15 text-red-400 px-2 py-0.5 rounded-full font-medium">SKIP</span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {item.fair === 0 ? "Available elsewhere for free or not needed" : `Fair price: $${item.fair} through your insurer`}
                  </p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-gray-500 line-through text-sm">${item.dealer.toLocaleString()}</p>
                  <p className="text-green-400 font-semibold text-sm">Save ${item.save.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-[#1e1e1e] p-6 bg-[#0a0a0a]">
            <div className="bg-amber-400/10 border border-amber-400/20 rounded-xl p-4">
              <p className="text-xs text-amber-400 font-semibold uppercase tracking-widest mb-2">Your script for GAP Insurance</p>
              <p className="text-gray-300 text-sm italic">"I'll pass on the GAP insurance today — I'm going to add it through my auto insurer for a fraction of the price."</p>
            </div>
          </div>
        </div>
        <p className="text-center text-gray-600 text-xs mt-4">Real analysis uses your actual menu. Results vary.</p>
      </section>

      {/* How it works */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              n: "1",
              title: "Take a photo",
              body: "In the finance office, photograph the add-on menu or worksheet they slide across the desk.",
            },
            {
              n: "2",
              title: "AI does the math",
              body: "Claude reads every line item, compares it to fair market rates, and flags what's overpriced.",
            },
            {
              n: "3",
              title: "Walk in with your script",
              body: "Get word-for-word sentences for each item so you know exactly what to say without hesitation.",
            },
          ].map(({ n, title, body }) => (
            <div key={n} className="bg-[#0f0f0f] border border-[#1e1e1e] rounded-2xl p-6">
              <div className="w-8 h-8 bg-amber-400/10 text-amber-400 font-bold rounded-lg flex items-center justify-center text-sm mb-4">
                {n}
              </div>
              <h3 className="font-semibold text-lg mb-2">{title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Truth bomb */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <div className="bg-[#0f0f0f] border border-[#1e1e1e] rounded-2xl p-8 md:p-12 text-center">
          <p className="text-5xl font-bold mb-4">40–80%</p>
          <p className="text-gray-400 text-lg max-w-xl mx-auto leading-relaxed">
            Commission an F&I manager earns on every add-on they sell you.
            They are not on your side. <span className="text-white">Now you have a tool that is.</span>
          </p>
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-5xl mx-auto px-6 pb-24 text-center">
        <h2 className="text-3xl font-bold mb-4">One price. One report. Done.</h2>
        <p className="text-gray-400 mb-10">No monthly fee. No account required. Pay once, get your full analysis instantly.</p>
        <div className="max-w-sm mx-auto bg-[#0f0f0f] border border-amber-400/30 rounded-2xl p-8">
          <p className="text-6xl font-bold mb-1">$19</p>
          <p className="text-gray-400 mb-8 text-sm">one-time payment</p>
          <ul className="text-left space-y-3 mb-8 text-sm text-gray-300">
            {[
              "Full breakdown of every add-on",
              "Fair market price for each item",
              "Word-for-word negotiation scripts",
              "Instant results via AI",
              "Works on any car dealer's menu",
            ].map((f) => (
              <li key={f} className="flex items-center gap-2">
                <span className="text-green-400 font-bold">✓</span> {f}
              </li>
            ))}
          </ul>
          <Link href="/analyze" className="block bg-amber-400 hover:bg-amber-300 text-black font-bold py-4 rounded-xl transition text-lg">
            Get My Report →
          </Link>
        </div>
      </section>

      <footer className="border-t border-[#111] text-center text-gray-700 py-8 text-sm">
        © 2026 FinalOffer · Not affiliated with any dealership or manufacturer
      </footer>

    </main>
  )
}
