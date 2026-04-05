import { NextRequest, NextResponse } from "next/server"
import Stripe from "stripe"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2024-06-20",
})

const PRICES: Record<string, { name: string; amount: number }> = {
  orchestrator: { name: "Productivity Orchestrator", amount: 2900 },
  curator: { name: "Intelli-Curator", amount: 1900 },
  guardian: { name: "Digital Guardian", amount: 2400 },
  bundle: { name: "Full Suite Bundle", amount: 6000 },
}

export async function POST(req: NextRequest) {
  const formData = await req.formData()
  const product = formData.get("product") as string

  const price = PRICES[product]
  if (!price) {
    return NextResponse.json({ error: "Invalid product" }, { status: 400 })
  }

  const baseUrl = process.env.NEXT_PUBLIC_URL || `https://${req.headers.get("host")}`

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    payment_method_types: ["card"],
    line_items: [
      {
        price_data: {
          currency: "usd",
          product_data: { name: price.name },
          unit_amount: price.amount,
          recurring: { interval: "month" },
        },
        quantity: 1,
      },
    ],
    success_url: `${baseUrl}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${baseUrl}/#pricing`,
  })

  return NextResponse.redirect(session.url!, 303)
}
