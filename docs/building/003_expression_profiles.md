# Adding expression data

Expression data should be processed using [LSTrAP](https://github.molgen.mpg.de/proost/LSTrAP), 
this will generate the expression matrix, coexpression networks and 
clusters that can be directly imported into CoNekt. Note that in 
some cases additional files, containing meta information, need to be 
provided.
 
## Adding expression profiles

In the 'Admin panel', under 'Add' -> 'Expression profiles'. Select the
species and the source (currently only LSTrAP expression matrices are supported). 

Next, select the expression matrix (generated using LSTrAP). Using a 
normalized (TPM or RPKM) matrix is strongly recommended !

Furthermore two additional files need to be provided, one that links the
run identifiers to specific conditions. This tab delimited file should 
be structured as indicated below, a one-line header (which is ignored) 
and two columns, the first with the sample ID and the second with a short
description of the condition sampled. Samples with the same description
will be treated as replicates ! Omitting the condition description will
exclude the sample from the profiles.


```
SampleID    ConditionDescription
SRR068987	Endosperm
SRR314813	Seedlings, 11 DAG
SRR314814	
SRR314815	Flowers (floral buds)
SRR314816
...
```

For profile plots on the website most likely a custum order of conditions
is preferred. (We usually order tissues from bottom to top) A file to 
specify this needs to be provided, conditions need to be stated in the 
orther they should appear in the plot.
Furthermore a color for that condition in the plot needs to be added in 
rgba() format. See the example below.

```
Roots (apex), 7 DAG	rgba(153, 51, 0, 0.5)
Roots (differentation zone), 4 DAP	rgba(153, 51, 0, 0.5)
Roots (elongation zone), 4 DAP	rgba(153, 51, 0, 0.5)
Roots (meristematic zone), 4 DAP	rgba(153, 51, 0, 0.5)
Roots (QC cells), 6 DAS	rgba(153, 51, 0, 0.5)
Roots (stele cells), 7 DAS	rgba(153, 51, 0, 0.5)
Roots (tip)	rgba(153, 51, 0, 0.5)
Leaves (rosette), 21 DAG	rgba(0, 153, 51, 0.5)
Leaves (rosette), 29 DAG	rgba(0, 153, 51, 0.5)
...
```

If all files are selected click 'Add Expression Profiles' to upload the
data and add everything to the database.


![Add expression profiles](../images/add_expression_profiles.png)