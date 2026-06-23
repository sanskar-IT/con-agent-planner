"""
Budget Agent — convention spending tracker.

Helps the user set a budget, log individual purchases, and retrieve a
spending summary.  Dollar amounts are always formatted as ``$X.XX``.

Note: persistent state (running totals, expense lists) lives in the ADK
session state managed by the orchestrator.  Tool functions here return
confirmation messages; the agent is instructed to maintain state via the
session context.
"""

from google.adk import Agent


# ── tool functions ──────────────────────────────────────────────────────

def set_budget(amount: float) -> str:
    """Set the user's convention budget to *amount*.

    Returns a confirmation message with the dollar-formatted value.
    The agent should persist this value in session state.
    """
    return f"Budget set to ${amount:.2f}. I'll track your spending against this limit."


def log_expense(item_name: str, cost: float) -> str:
    """Log a single purchase of *item_name* at *cost*.

    Returns a confirmation string.  The agent should update the running
    total in session state after calling this tool.
    """
    return (
        f"Logged expense: {item_name} — ${cost:.2f}. "
        "Remember to update the running total in your budget tracker."
    )


def get_budget_summary() -> str:
    """Request a budget summary.

    Because tool functions do not have direct access to ADK session state,
    this returns an instruction for the agent to compile the summary from
    its stored session data.
    """
    return (
        "Please compile the budget summary from session state. "
        "Include: total budget, total spent so far, remaining balance, "
        "and a list of logged expenses. Format all dollar amounts as $X.XX."
    )


# ── agent instance ──────────────────────────────────────────────────────

budget_agent = Agent(
    name="budget_agent",
    instruction=(
        "You track convention spending. Help the user set budgets, log "
        "purchases, and warn when expenses approach or exceed the budget. "
        "Always show dollar amounts formatted as $X.XX."
    ),
    tools=[
        set_budget,
        log_expense,
        get_budget_summary,
    ],
)
