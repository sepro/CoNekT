# PlaNet
Code to build PlaNet and set up the website

[Linux Installation instructions](docs/install_linux.md)

Building PlaNet
---------------

Default tables need to be populated

python build.py populate_go <FILE> : will add go terms from an OBO file to the database



PlaNet Website
--------------

PlaNet is a flask app, all that is required to start the website is running

    python run.py

To run this permanently on a server check the web on how to host a flask app using nginx or supervisor.

Contact
-------

  * Marek Mutwil ( mutwil@mpmpi-golm.mpg.de )
  * Sebastian Proost ( proost@mpimp-golm.mpg.de )

