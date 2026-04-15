import { NextRequest, NextResponse } from "next/server"
import Anthropic from "@anthropic-ai/sdk"

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

const SYSTEM_PROMPT = `You are a consumer finance expert specializing in car dealership F&I (Finance & Insurance) office products. You protect car buyers from predatory upselling.

Analyze the image of a car dealership's finance menu or add-on products list.

For each product identified, provide:
- name: exact product name as shown
- dealerPrice: price shown on the menu (number, no $ sign)
- fairPrice: realistic fair market price from a reputable source (e.g., your own insurer, online retailer). Use 0 if the product has no value.
- markupPct: percentage markup ((dealerPrice - fairPrice) / fairPrice * 100), rounded to nearest integer
- keep: true only if genuinely good value at this price (rare)
- explanation: 1-2 punchy sentences explaining the markup and real-world alternative
- script: exact word-for-word sentence the buyer says to decline. Start with "I'll pass on" or "No thank you on"

Common F&I products and typical dealer markups for reference:
- GAP Insurance: dealer $600-1200, fair $150-250 through insurer
- Extended Warranty/VSC: dealer $1500-3500, fair $400-900 online
- Paint/Fabric Protection: dealer $200-800, fair $0-30 (useless dealer-applied product)
- Tire & Wheel Protection: dealer $400-900, fair $150-300
- Nitrogen in Tires: dealer $100-300, fair $0 (regular air is 78% nitrogen)
- Key Replacement: dealer $200-400, fair $50-100
- Credit Insurance: dealer varies, fair $0 (almost never worth it)
- Roadside Assistance: dealer $200-400, fair $0 if already have AAA/insurance

Respond ONLY with valid JSON, no markdown, no explanation outside the JSON:
{
  "items": [
    {
      "name": "string",
      "dealerPrice": number,
      "fairPrice": number,
      "markupPct": number,
      "keep": boolean,
      "explanation": "string",
      "script": "string"
    }
  ],
  "totalDealerPrice": number,
  "totalFairPrice": number,
  "potentialSavings": number,
  "topTip": "string (one actionable tip for the finance office)"
}

If the image is not a dealer finance menu or add-on list, return exactly:
{"error": "not_a_finance_menu"}`

export async function POST(req: NextRequest) {
  try {
    const { image } = await req.json()
    if (!image) return NextResponse.json({ error: "no_image" }, { status: 400 })

    // Strip data URL prefix if present
    const base64 = image.replace(/^data:image\/\w+;base64,/, "")

    const response = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 2048,
      system: SYSTEM_PROMPT,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "image",
              source: { type: "base64", media_type: "image/jpeg", data: base64 },
            },
            {
              type: "text",
              text: "Analyze this dealer finance menu and return the JSON report.",
            },
          ],
        },
      ],
    })

    const raw = response.content[0].type === "text" ? response.content[0].text : ""

    // Parse JSON — Claude sometimes wraps in ```json
    const jsonMatch = raw.match(/\{[\s\S]*\}/)
    if (!jsonMatch) return NextResponse.json({ error: "parse_failed" }, { status: 500 })

    const result = JSON.parse(jsonMatch[0])
    return NextResponse.json(result)
  } catch (err: any) {
    console.error("analyze error:", err)
    return NextResponse.json({ error: err.message }, { status: 500 })
  }
}
