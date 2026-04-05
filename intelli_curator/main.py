#!/usr/bin/env python3
"""
Intelli-Curator: Personalized Insight & Learning Engine
Powered by Claude claude-opus-4-6 with extended thinking and tool use.
"""

import json
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
PROFILE_PATH = Path.home() / ".intelli_curator_profile.json"
KB_PATH = Path.home() / ".intelli_curator_kb.json"
MODEL = "claude-opus-4-6"

console = Console()
client = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# Profile & knowledge-base helpers
# ---------------------------------------------------------------------------

def load_profile() -> dict:
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text())
    return {}


def save_profile(profile: dict) -> None:
    PROFILE_PATH.write_text(json.dumps(profile, indent=2))


def load_kb() -> list[dict]:
    if KB_PATH.exists():
        return json.loads(KB_PATH.read_text())
    return []


def save_kb(kb: list[dict]) -> None:
    KB_PATH.write_text(json.dumps(kb, indent=2))


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_update_user_profile(field: str, value: Any) -> str:
    profile = load_profile()
    profile[field] = value
    save_profile(profile)
    return f"Profile updated: {field} = {value!r}"


def tool_get_user_profile() -> str:
    profile = load_profile()
    return json.dumps(profile, indent=2) if profile else "No profile found."


def tool_add_interest(interest: str, category: str) -> str:
    profile = load_profile()
    interests = profile.get("interests", [])
    if interest not in interests:
        interests.append(interest)
        profile["interests"] = interests
    expertise = profile.get("expertise_areas", [])
    if category and category not in expertise:
        expertise.append(category)
        profile["expertise_areas"] = expertise
    save_profile(profile)
    return f"Added interest '{interest}' under category '{category}'."


def tool_create_learning_path(topic: str, current_level: str, target_level: str, time_commitment_weeks: int) -> str:
    kb = load_kb()
    entry = {
        "id": str(uuid.uuid4())[:8],
        "title": f"Learning Path: {topic}",
        "content": (
            f"Topic: {topic}\n"
            f"Current level: {current_level}\n"
            f"Target level: {target_level}\n"
            f"Duration: {time_commitment_weeks} weeks"
        ),
        "category": topic,
        "tags": [topic, current_level, target_level, "learning-path"],
        "saved_at": datetime.utcnow().isoformat(),
        "type": "learning_path",
    }
    kb.append(entry)
    save_kb(kb)

    # track explored topics
    profile = load_profile()
    explored = profile.get("topics_explored", [])
    if topic not in explored:
        explored.append(topic)
        profile["topics_explored"] = explored
        save_profile(profile)

    return json.dumps(entry, indent=2)


def tool_save_insight(title: str, content: str, category: str, tags: list[str]) -> str:
    kb = load_kb()
    entry = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "content": content,
        "category": category,
        "tags": tags if isinstance(tags, list) else [tags],
        "saved_at": datetime.utcnow().isoformat(),
        "type": "insight",
    }
    kb.append(entry)
    save_kb(kb)
    return f"Insight saved with id={entry['id']}."


def tool_list_insights(filter_category: str = "", filter_tags: list[str] | None = None, limit: int = 10) -> str:
    kb = load_kb()
    results = kb
    if filter_category:
        results = [e for e in results if e.get("category", "").lower() == filter_category.lower()]
    if filter_tags:
        tags_lower = [t.lower() for t in filter_tags]
        results = [e for e in results if any(t.lower() in tags_lower for t in e.get("tags", []))]
    results = results[:limit]
    if not results:
        return "No insights found matching the filters."
    return json.dumps(results, indent=2)


def tool_search_knowledge_base(query: str, filter_type: str = "") -> str:
    kb = load_kb()
    q = query.lower()
    results = [
        e for e in kb
        if q in e.get("title", "").lower()
        or q in e.get("content", "").lower()
        or any(q in t.lower() for t in e.get("tags", []))
    ]
    if filter_type:
        results = [e for e in results if e.get("type") == filter_type]
    if not results:
        return "No matching entries found in the knowledge base."
    return json.dumps(results[:10], indent=2)


def tool_generate_daily_brief(focus_areas: list[str] | None = None) -> str:
    profile = load_profile()
    kb = load_kb()
    recent = sorted(kb, key=lambda e: e.get("saved_at", ""), reverse=True)[:5]
    areas = focus_areas or profile.get("interests", [])
    summary = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "user": profile.get("name", "Learner"),
        "focus_areas": areas,
        "goals": profile.get("learning_goals", []),
        "recent_insights_count": len(recent),
        "recent_titles": [e["title"] for e in recent],
        "topics_explored": profile.get("topics_explored", []),
    }
    return json.dumps(summary, indent=2)


def tool_recommend_topics(based_on: str = "interests") -> str:
    profile = load_profile()
    if based_on == "goals":
        base = profile.get("learning_goals", [])
    elif based_on == "recent":
        base = profile.get("topics_explored", [])[-5:]
    else:
        base = profile.get("interests", [])
    return json.dumps({"based_on": based_on, "seed_topics": base, "profile_depth": profile.get("preferred_depth", "intermediate")})


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOLS = [
    {"name": "update_user_profile", "description": "Update a field in the user's profile.", "input_schema": {"type": "object", "properties": {"field": {"type": "string"}, "value": {}}, "required": ["field", "value"]}},
    {"name": "get_user_profile", "description": "Retrieve the full user profile.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "add_interest", "description": "Add an interest and optional expertise category to the user profile.", "input_schema": {"type": "object", "properties": {"interest": {"type": "string"}, "category": {"type": "string", "default": ""}}, "required": ["interest"]}},
    {"name": "create_learning_path", "description": "Create and save a structured learning path for a topic.", "input_schema": {"type": "object", "properties": {"topic": {"type": "string"}, "current_level": {"type": "string"}, "target_level": {"type": "string"}, "time_commitment_weeks": {"type": "integer"}}, "required": ["topic", "current_level", "target_level", "time_commitment_weeks"]}},
    {"name": "save_insight", "description": "Save an insight, concept, or summary to the knowledge base.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "category": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}, "required": ["title", "content", "category", "tags"]}},
    {"name": "list_insights", "description": "List saved insights, optionally filtered.", "input_schema": {"type": "object", "properties": {"filter_category": {"type": "string", "default": ""}, "filter_tags": {"type": "array", "items": {"type": "string"}}, "limit": {"type": "integer", "default": 10}}}},
    {"name": "search_knowledge_base", "description": "Full-text search across the local knowledge base.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "filter_type": {"type": "string", "default": ""}}, "required": ["query"]}},
    {"name": "generate_daily_brief", "description": "Generate a structured daily briefing for the user.", "input_schema": {"type": "object", "properties": {"focus_areas": {"type": "array", "items": {"type": "string"}}}}},
    {"name": "recommend_topics", "description": "Suggest new topics based on the user's interests, goals, or recent activity.", "input_schema": {"type": "object", "properties": {"based_on": {"type": "string", "enum": ["interests", "goals", "recent"], "default": "interests"}}}},
]

TOOL_MAP = {
    "update_user_profile": lambda i: tool_update_user_profile(i["field"], i["value"]),
    "get_user_profile": lambda i: tool_get_user_profile(),
    "add_interest": lambda i: tool_add_interest(i["field"] if "field" in i else i.get("interest", ""), i.get("category", "")),
    "create_learning_path": lambda i: tool_create_learning_path(i["topic"], i["current_level"], i["target_level"], i["time_commitment_weeks"]),
    "save_insight": lambda i: tool_save_insight(i["title"], i["content"], i["category"], i.get("tags", [])),
    "list_insights": lambda i: tool_list_insights(i.get("filter_category", ""), i.get("filter_tags"), i.get("limit", 10)),
    "search_knowledge_base": lambda i: tool_search_knowledge_base(i["query"], i.get("filter_type", "")),
    "generate_daily_brief": lambda i: tool_generate_daily_brief(i.get("focus_areas")),
    "recommend_topics": lambda i: tool_recommend_topics(i.get("based_on", "interests")),
}
# Fix add_interest mapping to use correct key
TOOL_MAP["add_interest"] = lambda i: tool_add_interest(i.get("interest", ""), i.get("category", ""))


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def build_system_prompt(profile: dict) -> str:
    name = profile.get("name", "the user")
    depth = profile.get("preferred_depth", "intermediate")
    expertise = ", ".join(profile.get("expertise_areas", [])) or "general"
    interests = ", ".join(profile.get("interests", [])) or "various topics"
    goals = "; ".join(profile.get("learning_goals", [])) or "continuous learning"
    return f"""You are Intelli-Curator, a brilliant personal knowledge curator and learning coach. \
You know {name} deeply and tailor every response to their background.

User profile snapshot:
- Name: {name}
- Expertise: {expertise}
- Interests: {interests}
- Learning goals: {goals}
- Preferred depth: {depth}

Your responsibilities:
1. Curate personalized insights, summaries, and learning paths at the right depth ({depth}).
2. Proactively use your tools to save valuable insights, update the user's profile, and build learning paths.
3. On every session start, call generate_daily_brief and present a warm, tailored welcome.
4. When the user explores a topic, consider calling save_insight to persist key takeaways.
5. Recommend next steps and related topics using recommend_topics when appropriate.
6. Always write with clarity, intellectual depth, and genuine enthusiasm for the subject.
7. Use markdown formatting in your responses — headings, bullet lists, code blocks where relevant.
8. When reasoning through complex questions, think carefully before responding."""


# ---------------------------------------------------------------------------
# Agentic tool loop
# ---------------------------------------------------------------------------

def run_agent(messages: list[dict], profile: dict) -> str:
    """Run the full agentic loop: stream response, handle tool calls, return final text."""
    system = build_system_prompt(profile)
    final_text_parts: list[str] = []

    while True:
        collected_text = ""
        tool_uses: list[dict] = []
        current_tool: dict | None = None
        current_tool_input_raw = ""

        with client.messages.stream(
            model=MODEL,
            max_tokens=16000,
            thinking={"type": "adaptive", "budget_tokens": 8000},
            system=system,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                # Content block start
                if event.type == "content_block_start":
                    block = event.content_block
                    if block.type == "tool_use":
                        current_tool = {"id": block.id, "name": block.name, "input": {}}
                        current_tool_input_raw = ""
                    elif block.type == "text":
                        pass  # will accumulate via delta

                # Content block delta
                elif event.type == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta":
                        collected_text += delta.text
                        console.print(delta.text, end="", markup=False, highlight=False)
                    elif delta.type == "thinking_delta":
                        pass  # suppress raw thinking output
                    elif delta.type == "input_json_delta":
                        if current_tool is not None:
                            current_tool_input_raw += delta.partial_json

                # Content block stop
                elif event.type == "content_block_stop":
                    if current_tool is not None:
                        try:
                            current_tool["input"] = json.loads(current_tool_input_raw) if current_tool_input_raw else {}
                        except json.JSONDecodeError:
                            current_tool["input"] = {}
                        tool_uses.append(current_tool)
                        current_tool = None
                        current_tool_input_raw = ""

                # Message stop
                elif event.type == "message_stop":
                    pass

        if collected_text:
            console.print()  # newline after streamed text
            final_text_parts.append(collected_text)

        if not tool_uses:
            break  # no more tool calls — done

        # Build assistant message with all content blocks from the stream
        raw_message = stream.get_final_message()
        messages.append({"role": "assistant", "content": raw_message.content})

        # Execute tools and collect results
        tool_results = []
        for tu in tool_uses:
            tool_name = tu["name"]
            tool_input = tu["input"]
            console.print(f"\n[dim]  [tool] {tool_name}({', '.join(f'{k}={v!r}' for k, v in tool_input.items())})[/dim]")
            try:
                handler = TOOL_MAP.get(tool_name)
                result = handler(tool_input) if handler else f"Unknown tool: {tool_name}"
            except Exception as exc:
                result = f"Tool error: {exc}"
            tool_results.append({"type": "tool_result", "tool_use_id": tu["id"], "content": str(result)})

        messages.append({"role": "user", "content": tool_results})

    return "\n".join(final_text_parts)


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------

def onboard_user() -> dict:
    console.print(Panel("[bold cyan]Welcome to Intelli-Curator![/bold cyan]\nLet's build your personalized learning profile.", box=box.ROUNDED))
    name = Prompt.ask("[bold]What's your name?[/bold]")
    interests_raw = Prompt.ask("[bold]What are your main interests?[/bold] (comma-separated)")
    interests = [i.strip() for i in interests_raw.split(",") if i.strip()]
    expertise_raw = Prompt.ask("[bold]Areas of expertise?[/bold] (comma-separated, or press Enter to skip)", default="")
    expertise = [e.strip() for e in expertise_raw.split(",") if e.strip()]
    goals_raw = Prompt.ask("[bold]Learning goals?[/bold] (comma-separated)")
    goals = [g.strip() for g in goals_raw.split(",") if g.strip()]
    depth = Prompt.ask("[bold]Preferred depth?[/bold]", choices=["beginner", "intermediate", "expert"], default="intermediate")
    time_str = Prompt.ask("[bold]Daily learning time (minutes)?[/bold]", default="30")
    try:
        daily_time = int(time_str)
    except ValueError:
        daily_time = 30

    profile = {
        "name": name,
        "expertise_areas": expertise,
        "interests": interests,
        "learning_goals": goals,
        "preferred_depth": depth,
        "daily_time_minutes": daily_time,
        "topics_explored": [],
    }
    save_profile(profile)
    console.print(f"\n[green]Profile created for [bold]{name}[/bold]. Let's begin![/green]\n")
    return profile


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def show_profile(profile: dict) -> None:
    table = Table(title="Your Profile", box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    for key, val in profile.items():
        display = ", ".join(val) if isinstance(val, list) else str(val)
        table.add_row(key.replace("_", " ").title(), display)
    console.print(table)


def show_kb(kb: list[dict]) -> None:
    if not kb:
        console.print("[yellow]Knowledge base is empty.[/yellow]")
        return
    table = Table(title="Knowledge Base", box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Type", style="cyan", width=14)
    table.add_column("Title", style="white")
    table.add_column("Category", style="green")
    table.add_column("Saved", style="dim")
    for e in kb[-20:]:
        saved = e.get("saved_at", "")[:10]
        table.add_row(e.get("id", ""), e.get("type", ""), e.get("title", ""), e.get("category", ""), saved)
    console.print(table)


# ---------------------------------------------------------------------------
# Main REPL
# ---------------------------------------------------------------------------

def main() -> None:
    console.print(Panel(
        Text("Intelli-Curator", style="bold cyan", justify="center"),
        subtitle="[dim]Personalized Insight & Learning Engine[/dim]",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
    ))

    # Load or create profile
    profile = load_profile()
    if not profile:
        profile = onboard_user()

    # Conversation history
    messages: list[dict] = []

    # Startup: generate daily brief via Claude
    console.print("\n[bold cyan]Generating your personalized daily brief...[/bold cyan]\n")
    startup_prompt = (
        "Please greet me by name with a warm welcome, then call generate_daily_brief to review my current status. "
        "After getting the brief data, craft a concise, motivating daily brief that highlights my goals, "
        "recent activity, and 2-3 specific topic recommendations for today. Keep it inspiring and personal."
    )
    messages.append({"role": "user", "content": startup_prompt})

    with console.status("[dim]Thinking...[/dim]", spinner="dots"):
        pass  # brief pause for UX feel
    run_agent(messages, profile)

    # Help hint
    console.print(Panel(
        "[dim]Commands: [bold]profile[/bold] — view profile  |  [bold]kb[/bold] — browse knowledge base  |  [bold]quit[/bold] — exit\n"
        "Ask me anything to explore topics, create learning paths, or save insights.[/dim]",
        box=box.ROUNDED,
    ))

    # Interactive REPL
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        lower = user_input.lower()

        if lower in ("quit", "exit", "bye"):
            console.print("[cyan]Until next time! Keep learning.[/cyan]")
            break

        if lower == "profile":
            profile = load_profile()
            show_profile(profile)
            continue

        if lower == "kb":
            show_kb(load_kb())
            continue

        # Reload profile for freshness
        profile = load_profile()

        messages.append({"role": "user", "content": user_input})
        console.print(f"\n[bold magenta]Intelli-Curator[/bold magenta]  [dim]({MODEL})[/dim]\n")

        run_agent(messages, profile)

        # Keep context window manageable: trim to last 20 exchanges
        if len(messages) > 40:
            messages = messages[-40:]


if __name__ == "__main__":
    main()
