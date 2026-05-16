"""
Interactive CLI for the Nexus Consulting RAG assistant.

Usage:
    python src/cli.py
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from rag import RAGAssistant

console = Console()


def print_answer(result: dict) -> None:
    query_type = result["query_type"]
    sub_questions = result.get("sub_questions", [])

    # Query type badge
    badge_color = "cyan" if query_type == "simple" else "magenta"
    console.print(f"\n[{badge_color}]Query type: {query_type.upper()}[/{badge_color}]", end="")

    if sub_questions:
        console.print(f"  →  sub-questions: {len(sub_questions)}")
        for i, sq in enumerate(sub_questions, 1):
            console.print(f"   [{i}] {sq}", style="dim")
    else:
        console.print()

    # Answer
    console.print(
        Panel(
            result["answer"],
            title="[bold green]Answer[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # Sources table
    sources = result.get("sources", [])
    if sources:
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold blue")
        table.add_column("#", width=3)
        table.add_column("Document", style="cyan")
        table.add_column("Section", style="white")
        table.add_column("Score", width=7, justify="right")

        for i, src in enumerate(sources, 1):
            score = src["rerank_score"]
            score_color = "green" if score > 0 else "yellow" if score > -3 else "red"
            table.add_row(
                str(i),
                src["doc_title"],
                src["section"],
                f"[{score_color}]{score:.2f}[/{score_color}]",
            )

        console.print(table)


def main():
    console.print(
        Panel(
            "[bold]Nexus Consulting — Document Assistant[/bold]\n"
            "Ask questions about internal projects, clients, and team expertise.\n"
            "Type [bold cyan]exit[/bold cyan] or [bold cyan]quit[/bold cyan] to stop.",
            border_style="blue",
        )
    )

    console.print("\nInitializing retrieval system...", style="dim")
    assistant = RAGAssistant()
    console.print("[green]Ready.[/green]\n")

    while True:
        try:
            question = console.input("[bold yellow]Question:[/bold yellow] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            console.print("[dim]Goodbye.[/dim]")
            break
        if question.lower() in {"reset", "clear", "/reset"}:
            assistant.clear_history()
            console.print("[dim]Conversation history cleared.[/dim]\n")
            continue

        with console.status("[dim]Searching...[/dim]", spinner="dots"):
            result = assistant.answer(question)

        print_answer(result)
        console.print()


if __name__ == "__main__":
    main()
