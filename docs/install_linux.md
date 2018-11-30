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

CoNekT is based on Flask which offers various ways to run the site in production, an overview can be found 
[here](http://flask.pocoo.org/docs/1.0/deploying/) . 

We configured [CoNekT-Plants](http://conekt.mpimp-golm.mpg.de/pub/) with a [mysql database](connect_mysql.md) 
(recommended for production) and host it using Apache using this [configuration](apache_wsgi.md)  

