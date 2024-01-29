import typer


app = typer.Typer(
    name="tier1",
    help="Interactions with Tier1 instances.",
    )


@app.command()
def c1():
    """c1"""
    print('hello')
    

@app.command()
def c2():
    """c2"""    
    print('world')
