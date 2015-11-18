#Setting up mod_wsgi with Apache

Install apache and mod_wsgi for python 3

    sudo apt-get install apache2  libapache2-mod-wsgi-py3
    
Copy `planet.template.wsgi` to planet.wsgi and add the correct paths. 

    WSGI_PATH = 'location of your app'
    WSGI_ENV = 'location of activate_this.py, in the bin folder of the virtual environment'
    
Configure apache, example below can be added to the default VirtualHost. A valid user (non-admin) is required for this:

    # This part is optional, but will improve speed
    Alias /planet/static /path/to/planet/planet/static

    <Directory /path/to/planet/planet/static>
        Require all granted
    </Directory>
	
	# Set up WSGI
	WSGIDaemonProcess application user=user group=user threads=5
	WSGIScriptAlias /planet /path/to/planet.wsgi

	<Location /planet>
    	WSGIProcessGroup application
	    WSGIApplicationGroup %{GLOBAL}
	    Require all granted
	</Location>

