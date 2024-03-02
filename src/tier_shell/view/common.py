import typer


# Arguments

port_option = typer.Option(
    5000, 
    help='Application port.'
    )


uuid_option = typer.Option(
    '00000000-0000-0000-0000-000000000000',
    help='UUID or name of recipe to be launched. See \'RECIPES\' folder for recipe definitions',
    )

_NAME_TABLE = {
    "helloworld": "00000000-0000-0000-0000-000000000000",
    "loadtest": "00000000-0000-0000-0000-000000000111",
    "openrtist-cpu": "737b5001-d27a-413f-9806-abf9bfce6746",
    "openrtist-gpu": "755e5883-0788-44da-8778-2113eddf4271",
    }

def lookup_uuid(app_name: str) -> str:
    """Lookup UUID from app name."""
    return _NAME_TABLE.get(app_name)


app_id_option = typer.Option(
    'YpdTsMtb/QCdYKzHlzKkLcLzEbdTK0vP4ILmdcIvnhc=',
    help='Wireguard key for application.',
    )
