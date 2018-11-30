# CoNekT Windows Installation

## Getting Started


Python >= 3.3 is required with virtualenv

    [download python ](https://www.python.org/downloads/)


Clone the repository into a directory CoNekT using the Git Client for windows

Set up the virtual environment for a shell (without setuptools as there is a bug preventing this)

    virtualenv --no-setuptools CoNekT

Activate the virtual environment

    Scripts\activate

Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and run it in the CoNekT folder in the active
virtual environment to install pip and setuptools manually

    Scripts\python.exe get-pip.py

Install the requirements

    Scripts\pip.exe install -r requirements.txt

Copy the configuration template to config.py

    copy config.template.py config.py

Change settings in config.py

Remove get-pip.py

Build initial database

    # Point flask to the right script
    set FLASK_APP=run.py
    
    # Create the DB (with the initial admin account)
    # A bunch of SQL queries will be printed to the screen 
    flask initdb
    
    # Set up the migration
    # This will create a number of files and suggest to check and edit settings in alembic.ini 
    # You can do this if you wish, but it is not required
    # more info on alembic : https://alembic.sqlalchemy.org/en/latest/tutorial.html
    #
    # If you get an error that the folder already exists, remove the migrations folder or select another location by
    # adding "-d <new_folder>" to the command
    flask db init
    
    # Optional, create additional admin accounts
    flask add_admin <new_username> <new_password> 
    
    # Start the server locally
    flask run

You now have a fresh installation of CoNekT running locally on [http://localhost:5000](http://localhost:5000). 
How to fill it with your data is included in the section [Building CoNekT](building_conekt.md). 
