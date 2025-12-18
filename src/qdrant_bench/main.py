import os
import typer
import logfire
from qdrant_bench.presentation.cli.main import app as cli_app
from qdrant_bench.presentation.api.main import main as api_main

# Default to a local postgres container if not set
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/qdrant_bench")

app = typer.Typer()

@app.command()
def api():
    """Start the API server"""
    api_main()

@app.command()
def cli(name: str):
    """Run CLI commands"""
    # Initialize any necessary infrastructure for CLI here if needed
    # DatabaseEngine.init(DATABASE_URL) 
    cli_app(name)

def main():
    app()

if __name__ == "__main__":
    main()
