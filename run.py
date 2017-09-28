#!/usr/bin/env python3
import click
from planet import create_app, db
from planet.models.users import User

app = create_app('config')


@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')
    db.create_all(app=app)

    if len(User.query.all()) == 0:
        ADMIN_PASSWORD = app.config['ADMIN_PASSWORD']
        ADMIN_EMAIL = app.config['ADMIN_EMAIL']

        db.session.add(User("admin", ADMIN_PASSWORD, ADMIN_EMAIL, is_admin=True))
        db.session.commit()

        print("\nAn admin account has been created. Username=\'admin\' and password=\'" + ADMIN_PASSWORD + "\'")
        print("IMPORTANT: Change the password for this account")


@app.cli.command()
@click.argument('username', type=str)
@click.argument('password', type=str)
def add_user(username, password):
    if len(User.query.filter(User.username == username).all()) == 0:
        db.session.add(User(username, password, "", is_admin=False))
        db.session.commit()


@app.cli.command()
@click.argument('username', type=str)
@click.argument('password', type=str)
def add_admin(username, password):
    if len(User.query.filter(User.username == username).all()) == 0:
        db.session.add(User(username, password, "", is_admin=True))
        db.session.commit()

if __name__ == '__main__':
    app.run()
