#PlaNet Windows Installation

Getting Started
---------------

Python >= 3.3 is required with virtualenv

    [download python ](https://www.python.org/downloads/)


Clone the repository into a directory PlaNet using the Git Client for windows

Set up the virtual environment for a shell (without setuptools as there is a bug preventing this)

    virtualenv --no-setuptools PlaNet

Activate the virtual environment

    Scripts\activate

Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and run it in the PlaNet folder in the active
virtual environment to install pip and setuptools manually

    Scripts\python.exe get-pip.py

Install the requirements

    Scripts\pip.exe install -r requirements.txt

Copy the configuration template to config.py

    copy config.template.py config.py

Change settings in config.py

Remove get-pip.py

Build initial database

    Scripts\python.exe db_create.py

You now have a fresh installation of PlaNet. Follow instructions below to fill the database