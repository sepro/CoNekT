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
    flask initdb
    
    # Set up the migration
    flask db init
    
    # Optional, create additional admin accounts
    flask add_admin <new_username> <new_password> 

You now have a fresh installation of CoNekT. How to fill it with your data is included in the section [Building CoNekt](building_conekt.md)
