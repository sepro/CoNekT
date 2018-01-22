# Adding OrthoGroups with Trees and Gene Families

When building OrthoGroups and Gene families for CoNekT the easiest way to go about
this is to add the species to the database, and export the protein fastas from 
CoNekT. This ensures all IDs are the same.

## Importing OrthoGroups and Gene Families
Output from [OrthoFinder](https://github.com/davidemms/OrthoFinder) and (tribe)MCL can be directly imported, add a fitting 
description, select the type of data you wish to import and select the file. Hit 
**Add Families** to upload the file and create the gene families in the database.

For OrthoFinder, select Orthogroups.txt, from the output. For (tribe)MCL pick the 
file with the final output (all members of a gene family on one line).

![add_gf](../images/add_gf.png)

## Importing Trees

[OrthoFinder](https://github.com/davidemms/OrthoFinder)'s phylogenetic trees can
be imported into CoNekT. To do so **first create a gzip file** containing all the 
trees. Furthermore you will need to locate the file **SequenceIDs.txt** which is 
used to convert OrthoFinder's internal IDs back to CoNekT's.

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

