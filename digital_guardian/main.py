#!/usr/bin/env python3
"""
Proactive Digital Guardian - AI-powered security and privacy manager
Powered by Claude claude-opus-4-6 with extended thinking and tool use
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.prompt import Prompt
from rich.rule import Rule

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL = "claude-opus-4-6"
LOG_FILE = Path.home() / ".digital_guardian_log.json"
PROFILE_FILE = Path.home() / ".digital_guardian_profile.json"

console = Console()
client = anthropic.Anthropic()

BANNER = """
  ╔══════════════════════════════════════════════════════╗
  ║   /\\  PROACTIVE DIGITAL GUARDIAN  /\\               ║
  ║  /  \\  ─────────────────────────  \\  \\             ║
  ║ / /\\ \\ Powered by Claude claude-opus-4-6  \\ /\\ \\           ║
  ║/_/  \\_\\  AI Security & Privacy Shield  \\_/  \\_\\   ║
  ╚══════════════════════════════════════════════════════╝
"""

SYSTEM_PROMPT = """You are an expert cybersecurity analyst and privacy guardian powered by advanced AI.
Your role is to protect users from digital threats including phishing, scams, social engineering,
privacy violations, and other cyber risks.

When analyzing threats, you:
1. Identify specific indicators of compromise or malicious intent
2. Assess risk levels with clear justification
3. Provide actionable, practical recommendations
4. Explain technical concepts in plain language
5. Stay current on threat intelligence and attack patterns

Always use the available tools to structure your analysis and log findings. Be thorough but concise.
Risk levels: HIGH (immediate action needed), MEDIUM (caution warranted), LOW (minor concerns), SAFE (no significant threats).
"""

# ── Data Persistence ───────────────────────────────────────────────────────────

def load_json(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default
    return default


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2))


def get_log() -> list:
    return load_json(LOG_FILE, [])


def get_profile() -> dict:
    default = {
        "created": datetime.now().isoformat(),
        "analyzed_items": 0,
        "overall_score": 0,
        "recommendations": [],
        "checklist_completed": [],
    }
    return load_json(PROFILE_FILE, default)


def save_profile(profile: dict) -> None:
    save_json(PROFILE_FILE, profile)

# ── Tool Execution Functions ───────────────────────────────────────────────────

def execute_analyze_url(url: str, context: str = "") -> dict:
    indicators = []
    risk_score = 0

    suspicious_tlds = [".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click", ".download"]
    url_lower = url.lower()

    if any(tld in url_lower for tld in suspicious_tlds):
        indicators.append("Suspicious TLD associated with free/malicious domains")
        risk_score += 25

    if url.count(".") > 4:
        indicators.append("Excessive subdomains — common in URL obfuscation")
        risk_score += 20

    lookalike_brands = ["paypa1", "g00gle", "arnazon", "micros0ft", "app1e", "faceb00k", "netf1ix"]
    if any(brand in url_lower for brand in lookalike_brands):
        indicators.append("Brand impersonation detected in URL")
        risk_score += 40

    if "login" in url_lower and "http://" in url_lower:
        indicators.append("Login page served over unencrypted HTTP")
        risk_score += 35

    if url_lower.startswith("http://"):
        indicators.append("Unencrypted HTTP connection")
        risk_score += 15

    ip_pattern = any(c.isdigit() for c in url.split("/")[2].split(".")) if "/" in url else False
    if ip_pattern and "://" in url:
        domain = url.split("://")[1].split("/")[0]
        parts = domain.split(".")
        if len(parts) == 4 and all(p.isdigit() for p in parts):
            indicators.append("IP address used instead of domain name")
            risk_score += 30

    redirect_terms = ["redirect", "redir", "goto", "url=http", "link=http"]
    if any(term in url_lower for term in redirect_terms):
        indicators.append("Open redirect parameter detected")
        risk_score += 20

    risk_score = min(risk_score, 100)
    if risk_score >= 70:
        verdict = "HIGH RISK — Do not visit"
    elif risk_score >= 40:
        verdict = "MEDIUM RISK — Exercise caution"
    elif risk_score >= 15:
        verdict = "LOW RISK — Some concerns noted"
    else:
        verdict = "SAFE — No significant threats detected"

    recommendation = (
        "Block this URL immediately and report it as phishing." if risk_score >= 70
        else "Verify legitimacy through official channels before proceeding." if risk_score >= 40
        else "Proceed with caution; verify the site's SSL certificate." if risk_score >= 15
        else "URL appears safe. Always verify SSL before entering credentials."
    )

    event = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "type": "url_analysis",
        "input": url,
        "risk_level": ("high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low" if risk_score >= 15 else "safe"),
        "findings": indicators,
        "recommendation": recommendation,
        "score": risk_score,
    }
    log = get_log()
    log.append(event)
    save_json(LOG_FILE, log)

    profile = get_profile()
    profile["analyzed_items"] += 1
    save_profile(profile)

    return {"risk_score": risk_score, "indicators": indicators, "verdict": verdict, "recommendation": recommendation}


def execute_analyze_email(sender: str, subject: str, body_snippet: str,
                           has_attachments: bool, has_links: bool) -> dict:
    indicators = []
    risk_score = 0

    urgency_words = ["urgent", "immediate", "action required", "verify now", "suspended", "expires", "limited time", "act now"]
    combined = (subject + " " + body_snippet).lower()
    if any(w in combined for w in urgency_words):
        indicators.append("High urgency language creating pressure to act quickly")
        risk_score += 25

    brand_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    generic_domains = ["@gmail", "@yahoo", "@hotmail", "@outlook"]
    known_brands = ["paypal", "amazon", "apple", "microsoft", "google", "netflix", "bank", "irs", "fedex", "ups"]

    sender_lower = sender.lower()
    subject_lower = subject.lower()
    if any(brand in subject_lower for brand in known_brands) and any(gd in sender_lower for gd in generic_domains):
        indicators.append("Brand impersonation using free email provider")
        risk_score += 40

    if "@" in sender and sender_lower.count("@") == 1:
        domain = sender_lower.split("@")[1]
        if any(brand in subject_lower for brand in known_brands) and brand not in domain:
            indicators.append("Sender domain does not match claimed organization")
            risk_score += 35

    if has_attachments:
        risky_terms = ["invoice", "document", "receipt", "statement", "notice"]
        if any(t in combined for t in risky_terms):
            indicators.append("Attachment combined with financial/official document language")
            risk_score += 30

    if has_links and any(w in combined for w in ["click here", "verify", "confirm", "update your", "sign in"]):
        indicators.append("Suspicious call-to-action with embedded links")
        risk_score += 25

    reward_words = ["won", "winner", "prize", "reward", "gift card", "lottery", "selected"]
    if any(w in combined for w in reward_words):
        indicators.append("Reward/prize lure tactic detected")
        risk_score += 30

    risk_score = min(risk_score, 100)
    verdict = (
        "PHISHING — Delete immediately" if risk_score >= 70
        else "SUSPICIOUS — Verify before acting" if risk_score >= 40
        else "CAUTION — Review carefully" if risk_score >= 15
        else "LEGITIMATE — Appears safe"
    )
    action = (
        "Delete and report as phishing. Do not click any links or open attachments." if risk_score >= 70
        else "Contact the sender through official channels to verify before taking any action." if risk_score >= 40
        else "Review the email context carefully; avoid clicking links directly." if risk_score >= 15
        else "Email appears legitimate. Standard email hygiene still recommended."
    )

    event = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "type": "email_analysis",
        "input": f"From: {sender} | Subject: {subject}",
        "risk_level": ("high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low" if risk_score >= 15 else "safe"),
        "findings": indicators,
        "recommendation": action,
        "score": risk_score,
    }
    log = get_log()
    log.append(event)
    save_json(LOG_FILE, log)

    profile = get_profile()
    profile["analyzed_items"] += 1
    save_profile(profile)

    return {"risk_score": risk_score, "phishing_indicators": indicators, "verdict": verdict, "action": action}


def execute_analyze_message(platform: str, message_content: str, sender_info: str) -> dict:
    indicators = []
    risk_score = 0
    content_lower = message_content.lower()

    social_triggers = ["lonely", "beautiful", "attractive", "relationship", "investment opportunity",
                       "crypto", "bitcoin", "make money", "passive income"]
    if any(t in content_lower for t in social_triggers):
        indicators.append("Potential romance scam or investment fraud language")
        risk_score += 30

    impersonation_terms = ["irs", "fbi", "police", "court", "warrant", "arrest", "government",
                           "social security", "medicare", "customer support", "tech support"]
    if any(t in content_lower for t in impersonation_terms):
        indicators.append("Authority impersonation detected")
        risk_score += 40

    payment_terms = ["gift card", "wire transfer", "zelle", "cashapp", "venmo", "western union",
                     "send money", "payment", "bank account"]
    if any(t in content_lower for t in payment_terms):
        indicators.append("Suspicious payment method or financial request")
        risk_score += 35

    link_indicators = ["http://", "https://", "bit.ly", "tinyurl", "t.co", "goo.gl", "click here"]
    if any(li in content_lower for li in link_indicators):
        indicators.append("Embedded link in message — potential phishing vector")
        risk_score += 20

    if sender_info.lower() in ["unknown", "anonymous", "private number", ""]:
        indicators.append("Unverified/anonymous sender identity")
        risk_score += 15

    risk_score = min(risk_score, 100)
    verdict = (
        "SCAM — Block and report sender" if risk_score >= 70
        else "SUSPICIOUS — Do not engage further" if risk_score >= 40
        else "CAUTION — Verify sender identity" if risk_score >= 15
        else "LIKELY SAFE — No major threats detected"
    )

    event = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "type": "message_analysis",
        "input": f"[{platform}] {message_content[:100]}",
        "risk_level": ("high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low" if risk_score >= 15 else "safe"),
        "findings": indicators,
        "recommendation": verdict,
        "score": risk_score,
    }
    log = get_log()
    log.append(event)
    save_json(LOG_FILE, log)

    profile = get_profile()
    profile["analyzed_items"] += 1
    save_profile(profile)

    return {"risk_score": risk_score, "social_engineering_indicators": indicators, "verdict": verdict}


def execute_log_security_event(event_type: str, details: str, risk_level: str,
                                findings: list, recommendation: str) -> dict:
    event = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "input": details,
        "risk_level": risk_level,
        "findings": findings,
        "recommendation": recommendation,
        "score": {"high": 80, "medium": 50, "low": 20, "safe": 5}.get(risk_level, 0),
    }
    log = get_log()
    log.append(event)
    save_json(LOG_FILE, log)
    return {"status": "logged", "event_id": event["id"]}


def execute_get_security_report(time_period: str = "all", filter_risk_level: str = "") -> dict:
    log = get_log()
    now = datetime.now()
    cutoff = {
        "today": now - timedelta(days=1),
        "week": now - timedelta(weeks=1),
        "month": now - timedelta(days=30),
    }.get(time_period, datetime.min)

    filtered = [
        e for e in log
        if datetime.fromisoformat(e["timestamp"]) >= cutoff
        and (not filter_risk_level or e.get("risk_level") == filter_risk_level)
    ]

    counts = {"high": 0, "medium": 0, "low": 0, "safe": 0}
    for e in filtered:
        counts[e.get("risk_level", "safe")] += 1

    avg_score = (sum(e.get("score", 0) for e in filtered) / len(filtered)) if filtered else 0

    return {
        "period": time_period,
        "total_events": len(filtered),
        "risk_breakdown": counts,
        "average_risk_score": round(avg_score, 1),
        "recent_events": filtered[-5:],
    }


def execute_add_security_recommendation(category: str, recommendation: str,
                                         priority: str, resources: list) -> dict:
    profile = get_profile()
    rec = {
        "id": str(uuid.uuid4())[:8],
        "category": category,
        "recommendation": recommendation,
        "priority": priority,
        "resources": resources,
        "added": datetime.now().isoformat(),
        "completed": False,
    }
    profile["recommendations"].append(rec)
    save_profile(profile)
    return {"status": "added", "recommendation_id": rec["id"]}


def execute_check_password_strength(password: str) -> dict:
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 25
    elif len(password) >= 8:
        score += 15
        feedback.append("Use at least 12 characters for stronger security")
    else:
        feedback.append("Password is too short — use 12+ characters")

    if any(c.isupper() for c in password):
        score += 15
    else:
        feedback.append("Add uppercase letters")

    if any(c.islower() for c in password):
        score += 15
    else:
        feedback.append("Add lowercase letters")

    if any(c.isdigit() for c in password):
        score += 15
    else:
        feedback.append("Add numbers")

    special = set("!@#$%^&*()_+-=[]{}|;:,.<>?")
    if any(c in special for c in password):
        score += 20
    else:
        feedback.append("Add special characters (!@#$%^&*)")

    common = ["password", "123456", "qwerty", "admin", "letmein", "welcome", "monkey"]
    if password.lower() in common:
        score = 0
        feedback = ["This is a commonly known password — change it immediately"]

    strength = "STRONG" if score >= 80 else "MODERATE" if score >= 50 else "WEAK"
    return {"strength": strength, "score": score, "feedback": feedback, "note": "Password not stored or transmitted"}


def execute_generate_security_checklist(context: str) -> dict:
    checklists = {
        "personal": [
            "Enable two-factor authentication on all accounts",
            "Use a password manager (Bitwarden, 1Password)",
            "Review app permissions on mobile devices",
            "Enable full-disk encryption on devices",
            "Keep operating system and apps updated",
            "Use a VPN on public Wi-Fi",
            "Freeze your credit with all three bureaus",
            "Enable login notifications for critical accounts",
            "Regularly back up important data (3-2-1 rule)",
            "Audit connected third-party apps quarterly",
        ],
        "small_business": [
            "Implement employee security awareness training",
            "Deploy endpoint detection and response (EDR) tools",
            "Enforce multi-factor authentication company-wide",
            "Establish an incident response plan",
            "Perform regular security audits and penetration testing",
            "Implement data classification and handling policies",
            "Secure remote access with Zero Trust principles",
            "Maintain offsite encrypted backups",
            "Establish vendor security assessment process",
            "Deploy email filtering and anti-phishing tools",
        ],
        "developer": [
            "Implement secrets management (never hardcode credentials)",
            "Enable dependency vulnerability scanning (Dependabot, Snyk)",
            "Use SAST/DAST tools in CI/CD pipeline",
            "Sign commits with GPG keys",
            "Implement least-privilege access for service accounts",
            "Enable branch protection and code review requirements",
            "Scan container images for vulnerabilities",
            "Use HTTPS and enforce HSTS in web applications",
            "Implement proper logging and audit trails",
            "Conduct regular threat modeling sessions",
        ],
    }
    items = checklists.get(context, checklists["personal"])
    return {"context": context, "checklist": items, "total_items": len(items)}


def execute_get_threat_intelligence(topic: str) -> dict:
    intel = {
        "phishing": {
            "current_trends": ["AI-generated spear phishing emails", "QR code phishing (quishing)", "SMS phishing (smishing) surge"],
            "top_targets": ["Financial institutions", "Healthcare organizations", "Remote workers"],
            "mitigation": ["Email authentication (DMARC/DKIM/SPF)", "Security awareness training", "Anti-phishing browser extensions"],
        },
        "ransomware": {
            "current_trends": ["Double extortion (encrypt + leak data)", "RaaS (Ransomware-as-a-Service)", "Targeting backup systems first"],
            "top_targets": ["Healthcare", "Critical infrastructure", "SMBs with weak defenses"],
            "mitigation": ["Offline immutable backups", "Network segmentation", "Privileged access management"],
        },
        "data_breaches": {
            "current_trends": ["Credential stuffing at scale", "Third-party vendor compromises", "Insider threats increasing"],
            "top_targets": ["Any org with valuable PII", "Healthcare records", "Financial data"],
            "mitigation": ["Monitor HaveIBeenPwned", "Implement UEBA tools", "Data minimization practices"],
        },
        "social_engineering": {
            "current_trends": ["Deepfake voice/video calls", "LinkedIn-based pretexting", "AI chatbot impersonation"],
            "top_targets": ["HR and finance departments", "IT helpdesk personnel", "Executives (whaling)"],
            "mitigation": ["Out-of-band verification procedures", "Security culture training", "Strict callback verification"],
        },
    }
    topic_lower = topic.lower()
    for key, data in intel.items():
        if key in topic_lower or topic_lower in key:
            return {"topic": topic, **data}
    return {
        "topic": topic,
        "current_trends": ["AI-powered attacks increasing across all vectors", "Supply chain compromises growing"],
        "top_targets": ["All organizations and individuals"],
        "mitigation": ["Stay updated via CISA alerts", "Follow NIST cybersecurity framework"],
    }


def execute_review_privacy_settings(platform: str) -> dict:
    settings = {
        "google": {
            "key_settings": ["Activity Controls → pause Web & App Activity", "Ad Settings → opt out of personalization",
                              "Location History → disable", "Google Photos face recognition → disable",
                              "Review third-party app access at myaccount.google.com"],
            "privacy_url": "https://myaccount.google.com/privacy",
        },
        "facebook": {
            "key_settings": ["Privacy Checkup → restrict post audience to Friends", "Apps and Websites → remove unused apps",
                              "Face Recognition → disable", "Off-Facebook Activity → clear and disconnect",
                              "Location Services → disable"],
            "privacy_url": "https://www.facebook.com/settings?tab=privacy",
        },
        "linkedin": {
            "key_settings": ["Profile visibility → limit to connections", "Activity broadcasts → disable",
                              "Data privacy → download and review your data", "Advertising data → opt out of data sharing",
                              "Two-step verification → enable"],
            "privacy_url": "https://www.linkedin.com/psettings/",
        },
        "general": {
            "key_settings": ["Audit browser extensions — remove unused ones", "Review saved passwords in browser",
                              "Clear cookies and cache regularly", "Use privacy-focused browser (Firefox, Brave)",
                              "Enable DNS-over-HTTPS", "Review location permissions for all apps",
                              "Use tracker-blocking (uBlock Origin, Privacy Badger)"],
            "privacy_url": "https://www.privacyguides.org",
        },
    }
    platform_lower = platform.lower()
    for key, data in settings.items():
        if key in platform_lower:
            return {"platform": platform, **data}
    return settings["general"]

# ── Tool Dispatch ──────────────────────────────────────────────────────────────

TOOLS = [
    {"name": "analyze_url", "description": "Analyze a URL for phishing, malware, or scam indicators. Logs findings automatically.", "input_schema": {"type": "object", "properties": {"url": {"type": "string", "description": "The URL to analyze"}, "context": {"type": "string", "description": "Optional context about where this URL was found"}}, "required": ["url"]}},
    {"name": "analyze_email", "description": "Analyze an email for phishing indicators based on sender, subject, and content.", "input_schema": {"type": "object", "properties": {"sender": {"type": "string"}, "subject": {"type": "string"}, "body_snippet": {"type": "string"}, "has_attachments": {"type": "boolean"}, "has_links": {"type": "boolean"}}, "required": ["sender", "subject", "body_snippet", "has_attachments", "has_links"]}},
    {"name": "analyze_message", "description": "Analyze a text/social media message for social engineering, scams, or manipulation.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string"}, "message_content": {"type": "string"}, "sender_info": {"type": "string"}}, "required": ["platform", "message_content", "sender_info"]}},
    {"name": "log_security_event", "description": "Log a security event to the persistent security log.", "input_schema": {"type": "object", "properties": {"event_type": {"type": "string"}, "details": {"type": "string"}, "risk_level": {"type": "string", "enum": ["high", "medium", "low", "safe"]}, "findings": {"type": "array", "items": {"type": "string"}}, "recommendation": {"type": "string"}}, "required": ["event_type", "details", "risk_level", "findings", "recommendation"]}},
    {"name": "get_security_report", "description": "Retrieve a security report for a given time period.", "input_schema": {"type": "object", "properties": {"time_period": {"type": "string", "enum": ["today", "week", "month", "all"]}, "filter_risk_level": {"type": "string", "enum": ["", "high", "medium", "low", "safe"]}}, "required": []}},
    {"name": "add_security_recommendation", "description": "Add a security recommendation to the user's profile.", "input_schema": {"type": "object", "properties": {"category": {"type": "string"}, "recommendation": {"type": "string"}, "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]}, "resources": {"type": "array", "items": {"type": "string"}}}, "required": ["category", "recommendation", "priority", "resources"]}},
    {"name": "check_password_strength", "description": "Evaluate password strength without storing it.", "input_schema": {"type": "object", "properties": {"password": {"type": "string"}}, "required": ["password"]}},
    {"name": "generate_security_checklist", "description": "Generate a tailored security checklist.", "input_schema": {"type": "object", "properties": {"context": {"type": "string", "enum": ["personal", "small_business", "developer"]}}, "required": ["context"]}},
    {"name": "get_threat_intelligence", "description": "Get current threat intelligence on a security topic.", "input_schema": {"type": "object", "properties": {"topic": {"type": "string", "description": "E.g., phishing, ransomware, data_breaches, social_engineering"}}, "required": ["topic"]}},
    {"name": "review_privacy_settings", "description": "Get privacy settings guidance for a specific platform.", "input_schema": {"type": "object", "properties": {"platform": {"type": "string", "description": "E.g., google, facebook, linkedin, general"}}, "required": ["platform"]}},
]


def dispatch_tool(name: str, inputs: dict) -> str:
    fn_map = {
        "analyze_url": lambda i: execute_analyze_url(i["url"], i.get("context", "")),
        "analyze_email": lambda i: execute_analyze_email(i["sender"], i["subject"], i["body_snippet"], i["has_attachments"], i["has_links"]),
        "analyze_message": lambda i: execute_analyze_message(i["platform"], i["message_content"], i["sender_info"]),
        "log_security_event": lambda i: execute_log_security_event(i["event_type"], i["details"], i["risk_level"], i["findings"], i["recommendation"]),
        "get_security_report": lambda i: execute_get_security_report(i.get("time_period", "all"), i.get("filter_risk_level", "")),
        "add_security_recommendation": lambda i: execute_add_security_recommendation(i["category"], i["recommendation"], i["priority"], i.get("resources", [])),
        "check_password_strength": lambda i: execute_check_password_strength(i["password"]),
        "generate_security_checklist": lambda i: execute_generate_security_checklist(i["context"]),
        "get_threat_intelligence": lambda i: execute_get_threat_intelligence(i["topic"]),
        "review_privacy_settings": lambda i: execute_review_privacy_settings(i["platform"]),
    }
    result = fn_map[name](inputs)
    return json.dumps(result)

# ── Risk Display Helpers ───────────────────────────────────────────────────────

def risk_color(level: str) -> str:
    return {"high": "red", "medium": "yellow", "low": "cyan", "safe": "green"}.get(level.lower(), "white")


def risk_badge(level: str) -> Text:
    colors = {"high": ("bold white on red", "  HIGH RISK  "),
               "medium": ("bold black on yellow", "  MEDIUM RISK  "),
               "low": ("bold white on cyan", "  LOW RISK  "),
               "safe": ("bold white on green", "  SAFE  ")}
    style, label = colors.get(level.lower(), ("white", f"  {level.upper()}  "))
    return Text(label, style=style)

# ── Dashboard ──────────────────────────────────────────────────────────────────

def show_dashboard():
    console.print(Panel(BANNER, style="bold blue", box=box.DOUBLE))
    report = execute_get_security_report("week")
    profile = get_profile()

    table = Table(title="[bold cyan]Security Dashboard — Last 7 Days[/bold cyan]", box=box.ROUNDED, show_header=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    total = report["total_events"]
    breakdown = report["risk_breakdown"]
    table.add_row("Total Analyses", str(total))
    table.add_row("[red]High Risk[/red]", str(breakdown["high"]))
    table.add_row("[yellow]Medium Risk[/yellow]", str(breakdown["medium"]))
    table.add_row("[cyan]Low Risk[/cyan]", str(breakdown["low"]))
    table.add_row("[green]Safe[/green]", str(breakdown["safe"]))
    table.add_row("Avg Risk Score", f"{report['average_risk_score']}/100")
    table.add_row("Items Analyzed (Total)", str(profile.get("analyzed_items", 0)))
    pending = sum(1 for r in profile.get("recommendations", []) if not r.get("completed"))
    table.add_row("Pending Recommendations", str(pending))

    console.print(table)

    if report["recent_events"]:
        console.print("\n[bold]Recent Security Events:[/bold]")
        for ev in reversed(report["recent_events"][-3:]):
            ts = ev["timestamp"][:16].replace("T", " ")
            color = risk_color(ev.get("risk_level", "safe"))
            console.print(f"  [{color}]●[/{color}] [{ts}] {ev['type'].replace('_', ' ').title()} — {ev['input'][:60]}")

# ── Agentic Loop ───────────────────────────────────────────────────────────────

def run_claude(user_message: str):
    messages = [{"role": "user", "content": user_message}]
    console.print(Rule("[bold cyan]Guardian Analysis[/bold cyan]"))

    while True:
        response_text = []
        tool_calls = []
        current_tool = None
        thinking_shown = False

        with client.messages.stream(
            model=MODEL,
            max_tokens=16000,
            thinking={"type": "enabled", "budget_tokens": 8000},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                if hasattr(event, "type"):
                    if event.type == "content_block_start":
                        block = event.content_block
                        if block.type == "thinking" and not thinking_shown:
                            console.print("\n[dim italic]Reasoning through threat indicators...[/dim italic]")
                            thinking_shown = True
                        elif block.type == "tool_use":
                            current_tool = {"id": block.id, "name": block.name, "input_json": ""}
                    elif event.type == "content_block_delta":
                        delta = event.delta
                        if delta.type == "text_delta":
                            response_text.append(delta.text)
                            console.print(delta.text, end="", markup=False)
                        elif delta.type == "input_json_delta" and current_tool:
                            current_tool["input_json"] += delta.partial_json
                    elif event.type == "content_block_stop":
                        if current_tool:
                            tool_calls.append(current_tool)
                            current_tool = None

        if response_text:
            console.print()

        raw = stream.get_final_message()
        stop_reason = raw.stop_reason

        if stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": raw.content})
            tool_results = []

            for tc in tool_calls:
                try:
                    inputs = json.loads(tc["input_json"]) if tc["input_json"] else {}
                except json.JSONDecodeError:
                    inputs = {}

                console.print(f"\n[dim]⚙  Running tool: [bold]{tc['name']}[/bold][/dim]")
                result = dispatch_tool(tc["name"], inputs)
                result_data = json.loads(result)

                if tc["name"] in ("analyze_url", "analyze_email", "analyze_message"):
                    score = result_data.get("risk_score", 0)
                    level = "high" if score >= 70 else "medium" if score >= 40 else "low" if score >= 15 else "safe"
                    console.print(f"  Risk Assessment: ", end="")
                    console.print(risk_badge(level))

                tool_results.append({"type": "tool_result", "tool_use_id": tc["id"], "content": result})

            messages.append({"role": "user", "content": tool_results})

        else:
            break

    console.print(Rule())

# ── Menu ───────────────────────────────────────────────────────────────────────

def menu_analyze_url():
    url = Prompt.ask("[bold cyan]Enter URL to analyze[/bold cyan]")
    context = Prompt.ask("[dim]Where did you find this URL? (optional, press Enter to skip)[/dim]", default="")
    prompt = f"Analyze this URL for security threats: {url}"
    if context:
        prompt += f"\nContext: {context}"
    run_claude(prompt)


def menu_analyze_email():
    sender = Prompt.ask("[bold cyan]Sender email address[/bold cyan]")
    subject = Prompt.ask("[bold cyan]Email subject[/bold cyan]")
    body = Prompt.ask("[bold cyan]Paste a snippet of the email body[/bold cyan]")
    has_att = Prompt.ask("[cyan]Does it have attachments?[/cyan]", choices=["y", "n"]) == "y"
    has_links = Prompt.ask("[cyan]Does it contain links?[/cyan]", choices=["y", "n"]) == "y"
    prompt = (f"Analyze this email for phishing indicators:\n"
              f"Sender: {sender}\nSubject: {subject}\nBody snippet: {body}\n"
              f"Has attachments: {has_att}, Has links: {has_links}")
    run_claude(prompt)


def menu_analyze_message():
    platform = Prompt.ask("[bold cyan]Platform[/bold cyan]", default="SMS")
    sender = Prompt.ask("[bold cyan]Sender info (name, number, or 'unknown')[/bold cyan]")
    content = Prompt.ask("[bold cyan]Paste the message content[/bold cyan]")
    prompt = f"Analyze this message from [{platform}] for social engineering or scam indicators.\nSender: {sender}\nMessage: {content}"
    run_claude(prompt)


def menu_security_report():
    period = Prompt.ask("[bold cyan]Time period[/bold cyan]", choices=["today", "week", "month", "all"], default="week")
    run_claude(f"Generate a comprehensive security report for the {period} period. Include threat trends and recommendations.")


def menu_checklist():
    ctx = Prompt.ask("[bold cyan]Context[/bold cyan]", choices=["personal", "small_business", "developer"], default="personal")
    run_claude(f"Generate a security checklist for a {ctx} user and explain the most critical items.")


def menu_threat_intel():
    topic = Prompt.ask("[bold cyan]Threat topic[/bold cyan]", default="phishing")
    run_claude(f"Give me current threat intelligence and actionable defense strategies for: {topic}")


def menu_privacy():
    platform = Prompt.ask("[bold cyan]Platform to review[/bold cyan]", default="general")
    run_claude(f"Review privacy settings and provide step-by-step guidance for: {platform}")


def menu_freeform():
    question = Prompt.ask("[bold cyan]Ask the Digital Guardian anything[/bold cyan]")
    run_claude(question)

# ── Main Entry Point ───────────────────────────────────────────────────────────

def main():
    show_dashboard()

    menu = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    menu.add_column("Key", style="bold cyan", width=4)
    menu.add_column("Action", style="white")
    options = [("1", "Analyze URL"), ("2", "Analyze Email"), ("3", "Analyze Message/Text"),
               ("4", "Security Report"), ("5", "Security Checklist"), ("6", "Threat Intelligence"),
               ("7", "Privacy Settings Review"), ("8", "Ask the Guardian"), ("Q", "Quit")]
    for key, label in options:
        menu.add_row(f"[{key}]", label)

    handlers = {
        "1": menu_analyze_url, "2": menu_analyze_email, "3": menu_analyze_message,
        "4": menu_security_report, "5": menu_checklist, "6": menu_threat_intel,
        "7": menu_privacy, "8": menu_freeform,
    }

    while True:
        console.print("\n")
        console.print(Panel(menu, title="[bold cyan]Digital Guardian Menu[/bold cyan]", box=box.ROUNDED))
        choice = Prompt.ask("[bold]Select option[/bold]").strip().upper()

        if choice == "Q":
            console.print(Panel("[bold green]Stay safe out there. Guardian signing off.[/bold green]", box=box.ROUNDED))
            break
        elif choice in handlers:
            try:
                handlers[choice]()
            except KeyboardInterrupt:
                console.print("\n[yellow]Analysis cancelled.[/yellow]")
        else:
            console.print("[red]Invalid option. Please try again.[/red]")


if __name__ == "__main__":
    main()
