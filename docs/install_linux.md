#PlaNet Linux Installation

Getting Started
---------------

Python >= 3.3 and pip3 are required

    sudo apt-get install python3
    sudo apt-get install pip3

Install virtualenv

    sudo pip3 install virtualenv


Clone the repository into a directory PlaNet

    git clone https://github.molgen.mpg.de/proost/PlaNet PlaNet

Set up the virtual environment

    virtualenv --python=python3 PlaNet/

Activate the virtual environment

    cd PlaNet/
    source bin/activate

Install the requirements

    pip3 install -r requirements.txt

Copy the configuration template to config.py

    cp config.template.py config.py

Change settings in config.py

Build initial database

    python db_create.py

You now have a fresh installation of PlaNet. Follow instructions below to fill the database