# PlaNet Website

PlaNet is a flask app, all that is required to start the website is running. Note that the virtualenv needs to be 
set up and activated.

    python run.py
    
or using [cli](http://flask.pocoo.org/docs/0.12/cli/)

    export FLASK_APP=run.py
    flask run
    
    # or
    
    python -m flask run


This will run the website on port 5000 on localhost. Using an SSH tunnel this can be accessed remotely.

To run this permanently on a server check the web on how to host a flask app using [apache2](./apache_wsgi.md), nginx or supervisor.