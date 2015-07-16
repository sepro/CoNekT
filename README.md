# PlaNet
Code to build PlaNet and set up the website

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

Building PlaNet
---------------

TO DO add build instructions



PlaNet Website
--------------

PlaNet is a flask app, all that is required to start the website is running

    python run.py

To run this permanently on a server check the web on how to host a flask app using nginx or supervisor.

Contact
-------

  * Marek Mutwil ( mutwil@mpmpi-golm.mpg.de )
  * Sebastian Proost ( proost@mpimp-golm.mpg.de )

