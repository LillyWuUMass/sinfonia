from pathlib import Path
path = Path('./carbon/energy.csv')

path.parent.mkdir(parents=True, exist_ok=True)


with open("./carbon/energy.csv", "w") as f:
    pass
