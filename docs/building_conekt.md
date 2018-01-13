# Building CoNekt

## Using the admin panel to build CoNekt

Make sure *LOGIN_ENABLED=True* in *config.py* and the database was build 
with and admin account (check [here](install_linux.md) for instructions 
how to add an admin account). Next, go to the website, log in and (once logged
in) click on the username (admin) in the top right corner. Select 'Admin
Panel' from the drop-down menu.


![Admin panel](./images/admin_home.png "admin panel")

The Admin Panel will welcome you with a large warning. Deleting data, 
overwriting or changing entries here can ruin a carefully set up 
database. Make sure to read instructions on pages and this documentation
to avoid losing work. 

**When working with an existing database, make sure
to back up the database before proceeding.**

Step-by-step instructions

  * [Adding GO term and InterPro domain definitions](./building/001_GO_InterPro_domains.md)
  * [Adding a new species and functional data](./building/002_species_functional_data.md)
  * [Adding expression profiles](./building/003_expression_profiles.md)
  * [Adding co-expession networks and clusters](./building/004_coexpression_network_cluster.md)
  * [Adding comparative genomics data](./building/005_comparative_genomics.md)
  * [Precomputing counts and more](./building/006_precomputing_counts_etc.md)

