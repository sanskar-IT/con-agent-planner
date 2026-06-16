import typer
import subprocess
import sys
from agent import ConventionPlannerAgent
from session_service import DiscordSessionService
from rich.console import Console
from rich.panel import Panel

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


app = typer.Typer(help="Convention Planner ADK Root Agent CLI")
console = Console()

@app.command()
def query(
    text: str = typer.Argument(..., help="The message query to send to the agent"),
    session_id: str = typer.Option("default_session", "--session-id", "-s", help="The Discord Session ID")
):
    """
    Send a single query to the Convention Planner agent.
    """
    agent = ConventionPlannerAgent()
    console.print(Panel(f"[bold cyan]Input:[/bold cyan] {text}\n[bold cyan]Session ID:[/bold cyan] {session_id}", title="Query Details"))
    
    response = agent.process_message(session_id, text)
    
    console.print(Panel(response, title="Agent Response", border_style="green"))

@app.command()
def interactive(
    session_id: str = typer.Option("discord_user_1", "--session-id", "-s", help="The Discord Session ID")
):
    """
    Start an interactive chat session simulating a Discord channel.
    """
    agent = ConventionPlannerAgent()
    console.print(Panel(
        f"Simulating Discord session for user [bold yellow]{session_id}[/bold yellow].\n"
        "Type your messages below. Type 'exit' or 'quit' to end.",
        title="Interactive Session",
        border_style="yellow"
    ))
    
    while True:
        try:
            message = console.input("[bold green]You:[/bold green] ")
            if message.strip().lower() in ["exit", "quit"]:
                console.print("[yellow]Session closed.[/yellow]")
                break
            if not message.strip():
                continue
                
            response = agent.process_message(session_id, message)
            console.print(f"[bold blue]Agent:[/bold blue] {response}\n")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Session closed.[/yellow]")
            break

@app.command()
def test():
    """
    Run the automated evaluation test suite (pytest).
    """
    console.print("[bold cyan]Running evaluation test suite...[/bold cyan]")
    result = subprocess.run([".venv\\Scripts\\pytest", "test_evals.py"], capture_output=False)
    if result.returncode == 0:
        console.print("[bold green]All evaluations and guardrail tests passed successfully! (100% Override Precision)[/bold green]")
    else:
        console.print("[bold red]Some evaluations or guardrail tests failed.[/bold red]", style="bold red")

if __name__ == "__main__":
    app()
