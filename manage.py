from flask.cli import FlaskGroup
from arkiv_app import create_app

app = create_app()
cli = FlaskGroup(create_app=lambda: app)

if __name__ == '__main__':
    cli()
