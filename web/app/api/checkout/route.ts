import { NextRequest, NextResponse } from "next/server"
import Stripe from "stripe"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: "2024-06-20" })

const BASE_URL = process.env.NEXT_PUBLIC_URL || "https://web-two-phi-77.vercel.app"
const PRICE_ID = process.env.NEXT_PUBLIC_FINALOFFER_PRICE_ID || process.env.NEXT_PUBLIC_FAIRSEAT_PRICE_ID || ""

export async function POST(req: NextRequest) {
  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      line_items: [{ price: PRICE_ID, quantity: 1 }],
      mode: "payment",
      success_url: `${BASE_URL}/results?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${BASE_URL}/analyze`,
    })

    return NextResponse.json({ url: session.url })
  } catch (err: any) {
    console.error("checkout error:", err)
    return NextResponse.json({ error: err.message }, { status: 500 })
  }
}
