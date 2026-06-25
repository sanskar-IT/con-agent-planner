"""
Jarvis Convention Assistant — CLI entry point.

Commands:
    query       Send a single query
    interactive Start an interactive chat session
    plan        Show today's recommended itinerary
    status      Display current convention state for a session
    test        Run the automated evaluation test suite
"""

import typer
import subprocess
import sys
import runner
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = typer.Typer(help="Jarvis — Anime Convention Assistant CLI")
console = Console()


@app.command()
def query(
    text: str = typer.Argument(..., help="The message query to send to Jarvis"),
    session_id: str = typer.Option("default_session", "--session-id", "-s", help="The session ID"),
):
    """
    Send a single query to the Jarvis convention assistant.
    """
    console.print(Panel(
        f"[bold cyan]Input:[/bold cyan] {text}\n[bold cyan]Session ID:[/bold cyan] {session_id}",
        title="Query Details",
    ))

    response = runner.run(session_id, text)

    console.print(Panel(response, title="Jarvis Response", border_style="green"))


@app.command()
def interactive(
    session_id: str = typer.Option("user_1", "--session-id", "-s", help="The session ID"),
):
    """
    Start an interactive chat session with Jarvis.
    """
    console.print(Panel(
        f"Session [bold yellow]{session_id}[/bold yellow] started.\n"
        "Type your messages below. Type 'exit' or 'quit' to end.",
        title="🤖 Jarvis Convention Assistant",
        border_style="yellow",
    ))

    while True:
        try:
            message = console.input("[bold green]You:[/bold green] ")
            if message.strip().lower() in ["exit", "quit"]:
                console.print("[yellow]Session closed.[/yellow]")
                break
            if not message.strip():
                continue

            response = runner.run(session_id, message)
            console.print(f"[bold blue]Jarvis:[/bold blue] {response}\n")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Session closed.[/yellow]")
            break


@app.command()
def plan(
    session_id: str = typer.Option("default_session", "--session-id", "-s", help="The session ID"),
):
    """
    Show today's recommended convention itinerary.
    """
    from event_data_api import EventDataAPI

    console.print(Panel("📋 Generating today's plan...", title="Jarvis Planner", border_style="cyan"))

    metadata = EventDataAPI.get_metadata()
    schedule = EventDataAPI.get_schedule()

    if metadata:
        console.print(f"[bold]Convention:[/bold] {metadata.get('event', 'Unknown')}")
        console.print(f"[bold]Dates:[/bold] {metadata.get('dates', 'TBD')}")
        console.print(f"[bold]Location:[/bold] {metadata.get('location', 'TBD')}\n")

    if schedule:
        table = Table(title="📅 Official Schedule")
        table.add_column("Event", style="cyan", no_wrap=True)
        table.add_column("Time", style="green")
        table.add_column("Location", style="yellow")

        for event_name, details in schedule.items():
            table.add_row(
                event_name,
                details.get("time", "TBD"),
                details.get("location", "TBD"),
            )

        console.print(table)
    else:
        console.print("[yellow]No schedule data available yet.[/yellow]")

    console.print("\n[dim]All data from official EventDataAPI. Source tier: official_api.[/dim]")


@app.command()
def status(
    session_id: str = typer.Option("default_session", "--session-id", "-s", help="The session ID"),
):
    """
    Display the current convention state for a session.
    """
    from session_service import ConventionSessionService

    svc = ConventionSessionService()
    summary = svc.get_state_summary(session_id)

    table = Table(title=f"🔍 Session State: {session_id}")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    for key, value in summary.items():
        table.add_row(str(key), str(value))

    console.print(table)


@app.command()
def test():
    """
    Run the automated evaluation test suite (pytest).
    """
    console.print("[bold cyan]Running evaluation test suite...[/bold cyan]")
    result = subprocess.run([sys.executable, "-m", "pytest", "test_evals.py", "-v"], capture_output=False)
    if result.returncode == 0:
        console.print("[bold green]All evaluations and guardrail tests passed![/bold green]")
    else:
        console.print("[bold red]Some evaluations or guardrail tests failed.[/bold red]", style="bold red")


if __name__ == "__main__":
    app()
