"""
Autonomous Productivity Orchestrator
Powered by Claude claude-opus-4-6 with tool use and adaptive thinking.
"""

import json
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.columns import Columns
from rich import box

# ── Constants ────────────────────────────────────────────────────────────────

DATA_FILE = Path.home() / ".productivity_orchestrator_data.json"
MODEL = "claude-opus-4-6"
PRIORITY_COLORS = {"high": "red", "medium": "yellow", "low": "green"}
STATUS_COLORS = {"pending": "cyan", "in_progress": "yellow", "completed": "green"}

console = Console()
client = anthropic.Anthropic()

# ── Data persistence ──────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_tasks(tasks: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(tasks, indent=2))


# ── Tool implementations ──────────────────────────────────────────────────────

def tool_create_task(tasks: list[dict], title: str, description: str = "",
                     project: str = "General", priority: str = "medium",
                     due_date: str = "", tags: list[str] | None = None) -> dict:
    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "description": description,
        "project": project,
        "priority": priority,
        "status": "pending",
        "due_date": due_date,
        "created_at": datetime.now().isoformat(),
        "tags": tags or [],
    }
    tasks.append(task)
    save_tasks(tasks)
    return {"success": True, "task": task, "message": f"Task '{title}' created with ID {task['id']}."}


def tool_list_tasks(tasks: list[dict], filter_project: str = "",
                    filter_status: str = "", filter_priority: str = "") -> dict:
    results = tasks
    if filter_project:
        results = [t for t in results if t.get("project", "").lower() == filter_project.lower()]
    if filter_status:
        results = [t for t in results if t.get("status", "") == filter_status]
    if filter_priority:
        results = [t for t in results if t.get("priority", "") == filter_priority]
    return {"tasks": results, "count": len(results)}


def tool_update_task(tasks: list[dict], task_id: str, updates: dict) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            protected = {"id", "created_at"}
            for k, v in updates.items():
                if k not in protected:
                    task[k] = v
            save_tasks(tasks)
            return {"success": True, "task": task, "message": f"Task {task_id} updated."}
    return {"success": False, "message": f"Task {task_id} not found."}


def tool_complete_task(tasks: list[dict], task_id: str) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            save_tasks(tasks)
            return {"success": True, "message": f"Task '{task['title']}' marked as completed."}
    return {"success": False, "message": f"Task {task_id} not found."}


def tool_delete_task(tasks: list[dict], task_id: str) -> dict:
    original_len = len(tasks)
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) < original_len:
        tasks.clear()
        tasks.extend(remaining)
        save_tasks(tasks)
        return {"success": True, "message": f"Task {task_id} deleted."}
    return {"success": False, "message": f"Task {task_id} not found."}


def tool_draft_communication(communication_type: str, context: str,
                              recipient: str = "", tone: str = "professional") -> dict:
    # Returns a structured prompt result; actual drafting is done by Claude's reasoning
    return {
        "type": communication_type,
        "recipient": recipient,
        "tone": tone,
        "context_received": context,
        "instruction": (
            f"Draft a {tone} {communication_type} to '{recipient}' based on: {context}. "
            "Return only the final draft text."
        ),
    }


def tool_summarize_content(content: str, summary_type: str = "brief") -> dict:
    return {
        "content_length": len(content),
        "summary_type": summary_type,
        "instruction": f"Provide a {summary_type} summary of the following content: {content}",
    }


def tool_get_project_insights(tasks: list[dict], project: str = "all") -> dict:
    scope = tasks if project == "all" else [t for t in tasks if t.get("project", "").lower() == project.lower()]
    projects: dict[str, dict] = {}
    for task in scope:
        p = task.get("project", "General")
        if p not in projects:
            projects[p] = {"total": 0, "pending": 0, "in_progress": 0, "completed": 0,
                           "high_priority": 0, "overdue": 0}
        projects[p]["total"] += 1
        projects[p][task.get("status", "pending")] += 1
        if task.get("priority") == "high":
            projects[p]["high_priority"] += 1
        due = task.get("due_date", "")
        if due and due < datetime.now().strftime("%Y-%m-%d") and task.get("status") != "completed":
            projects[p]["overdue"] += 1
    return {
        "project_filter": project,
        "total_tasks": len(scope),
        "projects": projects,
        "completion_rate": (
            round(sum(1 for t in scope if t.get("status") == "completed") / len(scope) * 100, 1)
            if scope else 0
        ),
    }


# ── Tool dispatch ─────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "create_task",
        "description": "Create a new task and save it to the data store.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short task title"},
                "description": {"type": "string", "description": "Detailed description"},
                "project": {"type": "string", "description": "Project name"},
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_tasks",
        "description": "List tasks with optional filters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter_project": {"type": "string"},
                "filter_status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                "filter_priority": {"type": "string", "enum": ["high", "medium", "low"]},
            },
        },
    },
    {
        "name": "update_task",
        "description": "Update fields of an existing task by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "updates": {"type": "object", "description": "Dict of fields to update"},
            },
            "required": ["task_id", "updates"],
        },
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed.",
        "input_schema": {
            "type": "object",
            "properties": {"task_id": {"type": "string"}},
            "required": ["task_id"],
        },
    },
    {
        "name": "delete_task",
        "description": "Permanently delete a task by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"task_id": {"type": "string"}},
            "required": ["task_id"],
        },
    },
    {
        "name": "draft_communication",
        "description": "Draft an email, Slack message, or memo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "communication_type": {"type": "string", "enum": ["email", "slack", "memo"]},
                "context": {"type": "string"},
                "recipient": {"type": "string"},
                "tone": {"type": "string", "enum": ["professional", "casual", "formal", "friendly"]},
            },
            "required": ["communication_type", "context"],
        },
    },
    {
        "name": "summarize_content",
        "description": "Summarize provided text content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "summary_type": {"type": "string", "enum": ["brief", "detailed", "action_items"]},
            },
            "required": ["content"],
        },
    },
    {
        "name": "get_project_insights",
        "description": "Get statistics and insights for a project or all projects.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project name or 'all'"},
            },
        },
    },
]

SYSTEM_PROMPT = """You are the Autonomous Productivity Orchestrator — a proactive AI chief-of-staff.
Your job is to help the user stay on top of their work by managing tasks intelligently.

Behavior guidelines:
- Interpret natural language commands and map them to the right tool calls.
- After completing an operation, briefly confirm what you did.
- End EVERY response with a short "Suggestions:" section (1-3 bullet points) offering
  proactive next steps based on the current state of tasks or the conversation.
- When listing tasks, present them in a clear, organized way.
- When you notice overdue tasks, high-priority items, or imbalanced workloads, flag them.
- Keep responses concise but actionable. Today's date is """ + datetime.now().strftime("%Y-%m-%d") + "."


def dispatch_tool(name: str, inputs: dict, tasks: list[dict]) -> Any:
    if name == "create_task":
        return tool_create_task(tasks, **inputs)
    if name == "list_tasks":
        return tool_list_tasks(tasks, **inputs)
    if name == "update_task":
        return tool_update_task(tasks, **inputs)
    if name == "complete_task":
        return tool_complete_task(tasks, **inputs)
    if name == "delete_task":
        return tool_delete_task(tasks, **inputs)
    if name == "draft_communication":
        return tool_draft_communication(**inputs)
    if name == "summarize_content":
        return tool_summarize_content(**inputs)
    if name == "get_project_insights":
        return tool_get_project_insights(tasks, **inputs)
    return {"error": f"Unknown tool: {name}"}


# ── Rich UI helpers ───────────────────────────────────────────────────────────

def render_welcome() -> None:
    banner = Text()
    banner.append("Autonomous Productivity Orchestrator\n", style="bold cyan")
    banner.append("Powered by Claude claude-opus-4-6  •  Adaptive Thinking  •  Tool Use", style="dim")
    console.print(Panel(banner, border_style="cyan", padding=(1, 4)))


def render_task_summary(tasks: list[dict]) -> None:
    if not tasks:
        console.print(Panel("[dim]No tasks yet. Tell me what you're working on![/dim]",
                            title="Task Summary", border_style="dim"))
        return

    pending = sum(1 for t in tasks if t["status"] == "pending")
    in_prog = sum(1 for t in tasks if t["status"] == "in_progress")
    done = sum(1 for t in tasks if t["status"] == "completed")
    high = sum(1 for t in tasks if t["priority"] == "high" and t["status"] != "completed")
    today = datetime.now().strftime("%Y-%m-%d")
    overdue = sum(1 for t in tasks if t.get("due_date") and t["due_date"] < today
                  and t["status"] != "completed")

    stats = [
        f"[cyan]Pending:[/cyan] {pending}",
        f"[yellow]In Progress:[/yellow] {in_prog}",
        f"[green]Completed:[/green] {done}",
        f"[red]High Priority:[/red] {high}",
        f"[red]Overdue:[/red] {overdue}" if overdue else "[dim]No overdue tasks[/dim]",
    ]
    console.print(Panel(
        "  ".join(stats),
        title=f"[bold]Task Summary[/bold] — {len(tasks)} total",
        border_style="blue",
        padding=(0, 2),
    ))


def render_tool_call(name: str, inputs: dict) -> None:
    summary = ", ".join(f"{k}={repr(v)[:40]}" for k, v in list(inputs.items())[:3])
    console.print(f"  [dim][ tool: [bold]{name}[/bold]({summary}) ][/dim]")


def render_assistant_message(text: str) -> None:
    console.print(Panel(text.strip(), title="[bold cyan]Orchestrator[/bold cyan]",
                        border_style="cyan", padding=(1, 2)))


def render_thinking(text: str) -> None:
    # Show a collapsed indicator — full thinking is verbose
    lines = text.strip().splitlines()
    preview = lines[0][:80] + ("…" if len(lines[0]) > 80 or len(lines) > 1 else "")
    console.print(f"  [dim italic]Thinking: {preview}[/dim italic]")


def render_tasks_table(tasks: list[dict]) -> None:
    if not tasks:
        console.print("[dim]  (no tasks match the filter)[/dim]")
        return
    table = Table(box=box.ROUNDED, border_style="dim", show_lines=False,
                  header_style="bold blue")
    table.add_column("ID", style="dim", width=9)
    table.add_column("Title", min_width=20)
    table.add_column("Project", style="magenta")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Due", style="dim")

    for t in tasks:
        pri_color = PRIORITY_COLORS.get(t.get("priority", "medium"), "white")
        sta_color = STATUS_COLORS.get(t.get("status", "pending"), "white")
        table.add_row(
            t["id"],
            t["title"],
            t.get("project", "—"),
            f"[{pri_color}]{t.get('priority', 'medium')}[/{pri_color}]",
            f"[{sta_color}]{t.get('status', 'pending')}[/{sta_color}]",
            t.get("due_date", "—"),
        )
    console.print(table)


# ── Agentic loop ──────────────────────────────────────────────────────────────

def run_agent_turn(conversation: list[dict], tasks: list[dict], user_input: str) -> None:
    conversation.append({"role": "user", "content": user_input})

    while True:
        # Collect full streamed response
        response_content: list[dict] = []
        current_text = ""
        stop_reason = None

        with client.messages.stream(
            model=MODEL,
            max_tokens=16000,
            thinking={"type": "adaptive", "budget_tokens": 8000},
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=conversation,
        ) as stream:
            for event in stream:
                event_type = type(event).__name__

                if event_type == "ContentBlockStart":
                    block = event.content_block
                    if block.type == "thinking":
                        current_text = ""
                    elif block.type == "text":
                        current_text = ""
                    elif block.type == "tool_use":
                        current_text = ""

                elif event_type == "ContentBlockDelta":
                    delta = event.delta
                    delta_type = type(delta).__name__
                    if delta_type == "ThinkingDelta":
                        current_text += delta.thinking
                    elif delta_type == "TextDelta":
                        current_text += delta.text
                    elif delta_type == "InputJSONDelta":
                        current_text += delta.partial_json

                elif event_type == "ContentBlockStop":
                    # Peek at what block just closed via the accumulated stream message
                    pass

            # Get the final structured message
            final_message = stream.get_final_message()
            stop_reason = final_message.stop_reason
            response_content = [
                block.model_dump() for block in final_message.content
            ]

        # Display content blocks
        has_text = False
        for block in response_content:
            if block["type"] == "thinking":
                render_thinking(block.get("thinking", ""))
            elif block["type"] == "text":
                text = block.get("text", "").strip()
                if text:
                    render_assistant_message(text)
                    has_text = True
            elif block["type"] == "tool_use":
                render_tool_call(block["name"], block.get("input", {}))

        # Append assistant turn to conversation
        conversation.append({"role": "assistant", "content": response_content})

        if stop_reason != "tool_use":
            break

        # Execute all tool calls and collect results
        tool_results = []
        for block in response_content:
            if block["type"] != "tool_use":
                continue
            tool_name = block["name"]
            tool_input = block.get("input", {})
            try:
                result = dispatch_tool(tool_name, tool_input, tasks)
                # If the result contains a list of tasks, render them inline
                if isinstance(result, dict) and "tasks" in result:
                    render_tasks_table(result["tasks"])
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": json.dumps(result),
                })
            except Exception as exc:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": json.dumps({"error": str(exc)}),
                    "is_error": True,
                })

        conversation.append({"role": "user", "content": tool_results})


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    render_welcome()

    tasks: list[dict] = load_tasks()
    render_task_summary(tasks)

    console.print(
        "\n[dim]Type a natural language command (e.g. 'Add a high-priority task to review Q1 report')."
        "\nType [bold]quit[/bold] or [bold]exit[/bold] to end the session.[/dim]\n"
    )

    conversation: list[dict] = []

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "q"}:
            console.print(Panel(
                "[bold cyan]Goodbye![/bold cyan]  Your tasks are saved. "
                f"You have [yellow]{sum(1 for t in tasks if t['status'] != 'completed')}[/yellow] "
                "open tasks.",
                border_style="cyan",
            ))
            break

        try:
            run_agent_turn(conversation, tasks, user_input)
        except anthropic.APIError as exc:
            console.print(f"[red]API error:[/red] {exc}")
        except Exception as exc:
            console.print(f"[red]Unexpected error:[/red] {exc}")
            raise

        console.print()  # breathing room between turns


if __name__ == "__main__":
    main()
