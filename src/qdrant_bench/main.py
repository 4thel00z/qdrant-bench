import os

import typer

from qdrant_bench.presentation.api.main import main as api_main
from qdrant_bench.presentation.cli.main import app as cli_app

# Default to a local postgres container if not set
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/qdrant_bench")

app = typer.Typer()

# Mount the CLI tools as a subcommand group
app.add_typer(cli_app, name="tools", help="Run various CLI tools and utilities.")

@app.command(name="api", help="Start the Qdrant Bench API server.")
@app.command(name="run", help="Alias for 'api'. Start the API server.")
@app.command(name="serve", help="Alias for 'api'. Start the API server.")
def api():
    """Start the API server."""
    api_main()

def main():
    app()

if __name__ == "__main__":
    main()
