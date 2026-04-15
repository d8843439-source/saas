import { NextRequest, NextResponse } from "next/server"
import Stripe from "stripe"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: "2024-06-20" })

export async function GET(req: NextRequest) {
  const sessionId = req.nextUrl.searchParams.get("session_id")
  if (!sessionId) return NextResponse.json({ verified: false }, { status: 400 })

  try {
    const session = await stripe.checkout.sessions.retrieve(sessionId)
    const verified = session.payment_status === "paid"
    return NextResponse.json({ verified })
  } catch (err: any) {
    return NextResponse.json({ verified: false, error: err.message }, { status: 400 })
  }
}
