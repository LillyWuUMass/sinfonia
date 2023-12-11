import typer


port_option = typer.Option(
    5000, 
    help='Application port.'
    )
uuid_option = typer.Option(
    '00000000-0000-0000-0000-000000000000', 
    help='UUID of recipe to be launched. See \'RECIPES\' folder for recipe definitions'
    )
app_id_option = typer.Option(
    'YpdTsMtb/QCdYKzHlzKkLcLzEbdTK0vP4ILmdcIvnhc=', 
    help='UUID of recipe to be launched. See \'RECIPES\' folder for recipe definitions'
    )
