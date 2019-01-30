# Adding OrthoGroups with Trees and Gene Families

When building OrthoGroups and Gene families for CoNekT the easiest way to go about
this is to add the species to the database, and export the protein fastas from 
CoNekT. This ensures all IDs are the same.

## Importing OrthoGroups and Gene Families
Output from [OrthoFinder 1.1.x](https://github.com/davidemms/OrthoFinder/releases/tag/1.1.10) and (tribe)MCL can be directly imported. To do so, enter a description, select the type of data you wish to import and select the required file (see below). Hit 
**Add Families** to upload the file and create the gene families in the database.

For OrthoFinder, select Orthogroups.txt, from the output directory. For (tribe)MCL pick the 
file with the final output (all members of a gene family on one line).

![add_gf](../images/add_gf.png)

## Importing Trees (OrthoFinder 1.1.x only)

[OrthoFinder 1.1.x](https://github.com/davidemms/OrthoFinder/releases/tag/1.1.10)'s phylogenetic trees can
be imported into CoNekT. To do so **first create a tar gzip file, with a .tgz extension** containing all the 
**rooted** trees (and only those trees), these can be found in the **working directory** (and have the word rooted in their filenames). In linux this can be done using the [*tar* command](https://www.howtogeek.com/248780/how-to-compress-and-extract-files-using-the-tar-command-on-linux/), windows users can use [7-zip](https://www.7-zip.org/), a free tool to create archives, to create this file.

Furthermore you will need to locate the file **SequenceIDs.txt** which is 
used to convert OrthoFinder's internal IDs back to CoNekT's.

Note on OrthoFinder >= 2.0: OrthoFinder 2.0 and above changed the way trees are handled and stores the trees in a different format. This is currently not supported by CoNekT.

![add_trees](../images/add_trees.png)

First select the **OrthoFinder families** you wish to add trees to. Next **add a
description** and finally select the **gzip file** with all trees and 
**SequenceIDs.txt**.

Currently adding trees to other types of gene families is not supported.

## Adding Clades

For clades to be detected correctly, clade definitions need to be stored in the 
database from 'Add->'Clades'. This is done using a JSON object structured as the
example here:

```json
{
    "Arabidopsis": {
        "species": ["ath"],
        "tree": null
    },
    "Poplar": {
        "species": ["ptr"],
        "tree": null
    },
    "Rice": {
        "species": ["osa"],
        "tree": null
    },
    "Rosids": {
        "species": ["ptr", "ath"],
        "tree": "(ptr:0.01, ath:0.01);"
    },
    "Angiosperms": {
        "species": ["ptr", "ath", "osa"],
        "tree": "((ptr:0.03, ath:0.03):0.01, osa:0.04);"
    }
}
```

**Dictionary keys** are different clades, within each dict you have to specify two 
things : the **species**, which contain an array of short names of the species in that
clade and a **tree** with a newick tree of that clade.

## Tree Reconciliation

Once trees are correctly uploaded to the database and the clades are defined, the tree reconsiliation can be started from the the admin panel's menu under : 'Build'->'Reconcile Trees'
