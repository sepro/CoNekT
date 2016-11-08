# Building PlaNet

## Using the admin panel to build PlaNet 2.0

Make sure *LOGIN_ENABLED=True* in *config.py* and the database was build 
with and admin account. Next, go to the website, log in and (once logged
in) click on the username (admin) in the top right corner. Select 'Admin
Panel' from the drop-down menu.


![Admin pane](./images/admin_home.png "admin panel")

The Admin Panel will welcome you with a large warning. Deleting data, 
overwriting or changing entries here can ruin a carefully set up 
database. Make sure to read instructions on pages and this documentation
to avoid losing work. When working with an existing database, make sure
to back up the database before proceeding.

### Adding GO terms and InterPro domains

Descriptions for GO terms and InterPro domains should be added before
adding functional annotation. This step should be completed first. In
the top menu click on 'Add' and select 'Functional Data'. 
 
![Add functional data](./images/add_functional_data.png "Adding functional data")

The GO descriptions can be obtained from the Gene Ontology Consortium's 
official website in OBO format [here](http://geneontology.org/page/download-ontology).
InterPro domains and descriptions (called the **Entry list**) are found on EBI InterPro's download pages [here](https://www.ebi.ac.uk/interpro/download.html), 
decompress the .gz file prior to uploading. 

Click the buttons on the page and select the corresponding files, next 
click 'Add functional data' to upload the files to your server and 
import them in the database. This process can take some time, do not 
close the browser window. 

**Note: The existing tables will be cleared before adding the new 
definitions. Do not update this information if GO/InterPro data is 
already added to species !**


### Adding a new species



## Using the build script

*UNDER CONSTRUCTION*