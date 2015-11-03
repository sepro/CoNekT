#Setting up MySQL/MariaDB for Planet

Either use the libmysql library which needs to be installed on the machine using

    sudo apt-get install python3-dev libmysqlclient-dev

and within the virtualenvironment
 
    pip install mysqlclient
 
In the config file the connection needs to be set up using :

    SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@ip_address/database'


In case the **libraries cannot be installed** on the machine a pure python mysql connector can be used. Install this within
the virtual environment

    pip install PyMySQL

In the config file the connection needs to be set up using :

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@ip_address/database'