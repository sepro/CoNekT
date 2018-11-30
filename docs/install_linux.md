# CoNekT Linux Installation

## Getting Started

Python >= 3.3 and pip3 are required

    sudo apt-get install python3
    sudo apt-get install pip3

Install virtualenv

    sudo pip3 install virtualenv


Clone the repository into a directory CoNekT

    git clone https://github.com/sepro/CoNekT CoNekT

Set up the virtual environment

    virtualenv --python=python3 CoNekT/

Activate the virtual environment

    cd CoNekT/
    source bin/activate

Install the requirements

    pip3 install -r requirements.txt

Copy the configuration template to config.py

    cp config.template.py config.py

Change settings in config.py. **Apart from configuring paths, also change the secret key and the admin password !**

Build initial database

    # Point flask to the right script
    export FLASK_APP=run.py
    
    # Create the DB (with the initial admin account)
    flask initdb
    
    # Set up the migration
    flask db init
    
    # Optional, create additional admin accounts
    flask add_admin <new_username> <new_password> 
    

You now have a fresh installation of CoNekT. How to fill it with your data is included in the section [Building CoNekT](building_conekt.md)
