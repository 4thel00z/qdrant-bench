import logfire
import typer

# Create a new Typer app for CLI tools.
# We don't call logfire.configure() here to avoid side effects when importing;
# it should be configured in the main entry point.
app = typer.Typer()

@app.command()
def hello(name: str):
    """Simple hello world command."""
    logfire.info(f"Hello command called with name={name}")
    print(f"Hello {name}")

if __name__ == "__main__":
    logfire.configure()
    app()
