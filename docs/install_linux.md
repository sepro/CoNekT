# CoNekt Linux Installation

## Getting Started

Python >= 3.3 and pip3 are required

    sudo apt-get install python3
    sudo apt-get install pip3

Install virtualenv

    sudo pip3 install virtualenv


Clone the repository into a directory CoNekt

    git clone https://github.molgen.mpg.de/proost/CoNekt CoNekt

Set up the virtual environment

    virtualenv --python=python3 CoNekt/

Activate the virtual environment

    cd PlaNet/
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
    

You now have a fresh installation of CoNekt. How to fill it with your data is included in the section [Building CoNekt](building_conekt.md)