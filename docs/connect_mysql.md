#Setting up MySQL/MariaDB for Planet

Either use the libmysql library which needs to be installed on the machine using

    sudo apt-get install python3-dev libmysqlclient-dev

and within the virtualenvironment
 
    pip install mysqlclient
 
In the config file the connection needs to be set up using :

    SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@ip_address/database'


In case the **libraries cannot be installed** on the machine a pure python mysql connector can be used. Install this within
the virtual environment. 

    pip install PyMySQL

In the config file the connection needs to be set up using :

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@ip_address/database'
    
    
## Setting up the database using the MySQL CLI

First create a database. The character set and collate are important as sqlalchemy-migrate doesn't work with utf8mb4 (the
default).

    CREATE DATABASE planet_db_01 CHARACTER SET latin1 COLLATE latin1_general_ci;
    
Give permissions to a user (planet_dev in this example) to access the database:

    GRANT INDEX, CREATE, DROP, SELECT, UPDATE, DELETE, ALTER, EXECUTE, INSERT on planet_db_01.* TO planet_dev@localhost;