import logfire
import typer

app = typer.Typer()
logfire.configure()

@app.command()
def hello(name: str):
    logfire.info(f"Hello command called with name={name}")
    print(f"Hello {name}")

if __name__ == "__main__":
    app()

