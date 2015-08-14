# Instruction for Developers

## Code Structure


Two major packages are included **build** and **planet**. The former contains parsers and other code to fill the
database. The latter contains all the code to run the platform and is structured as a Model-Template-Controller.

### planet package

#### planet/__init__.py

This is the place where all important objects are set up. The app is created here, the database is started,  models and
controllers are loaded here and controllers registered as blueprints. **When new models or controllers are added to
the project they need to be included here!**

Flask packages like Flask-Login, Flask-Admin and Flask-DebugToolbar are initialized here.

## Database Maintenance


In case there are changes to the Models a migration script can and should be generated using **db_migrate.py**.
This will create a file in **migration/versions/** which should be committed to the repository (after manual inspection).

To apply the new changes to an existing database run **db_upgrade**.