# Instruction for Developers

Code Structure
--------------

Two major packages are included **build** and **planet**. The former contains parsers and other code to fill the
database. The latter contains all the code to run the platform and is structured as a Model-Template-Controller.


Database Maintenance
--------------------

In case there are changes to the Models a migration script can and should be generated using **db_migrate.py**.
This will create a file in **migration/versions/** which should be committed to the repository (after manual inspection).

To apply the new changes to an existing database run **db_upgrade**.