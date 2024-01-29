import typer


app = typer.Typer()


@app.command()
def c1():
    """c1"""
    print('hello')
    

@app.command()
def c2():
    """c2"""    
    print('world')
