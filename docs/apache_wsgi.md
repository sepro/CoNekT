# Setting up mod_wsgi with Apache

Install apache and mod_wsgi for python 3

    sudo apt-get install apache2  libapache2-mod-wsgi-py3
    
Copy `conekt.template.wsgi` to conekt.wsgi and add the correct paths. 

    WSGI_PATH = 'location of your app'
    WSGI_ENV = 'location of activate_this.py, in the bin folder of the virtual environment'

When using the built-in venv module in Python 3.6 and up activate_this.py is no longer automatically included in 
the virtual environment and needs to be added manually. You can find it [here](https://github.com/pypa/virtualenv/blob/master/virtualenv_embedded/activate_this.py)
    
Configure apache, example below can be added to the default VirtualHost. A valid user (non-admin), usually www-data, is required for this:

    # This part is optional, but will improve speed
    Alias /conekt/static /path/to/conekt/static

    <Directory /path/to/conekt/static>
        Require all granted
    </Directory>
	
	# Set up WSGI
	WSGIDaemonProcess application user=user group=user threads=5
	WSGIScriptAlias /conekt /path/to/conekt.wsgi

	<Location /conekt>
        WSGIProcessGroup application
	    WSGIApplicationGroup %{GLOBAL}
	    Require all granted
	</Location>

