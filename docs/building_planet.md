# Building PlaNet

The script build.py can be used to parse most data types and add the results to the database. Make sure all
code is properly installed and that a database is created.

Add functional annotation
-------------------------
First a list of all possible GO terms, their description and structure needs to be added to the database. An OBO file
can be found on [Gene Ontology](http://geneontology.org/), to add the file to the database use the command below.


    python build.py populate_go <FILE> : will add go terms from an OBO file to the database
