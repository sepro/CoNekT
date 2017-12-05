# Tutorial: Compare Specificity

Tissue specificity can be combined with gene families to pick up genes with conserved expression between species but
also to detect genes within one species that sub- or neo-functionalized after duplication. Look at the examples below to
see how.


## Conserved Expression

Some low-abudant genes can cause false positives when looking for tissue/condition specificity. These adverse results can
be greatly reduced by looking for genes that are specific in a certain tissue in one species and have an ortholog 
(or homolog) specifically for the corresponding tissue is another species.

In this example *Arabidopsis thaliana* silique specific genes are matched with their orthologs expressed specifically in
Tomato (*Solanum lycopersicum*) fruis. This feature is available from the tools menu below the button 
**Compare specificity**. The SPM (Specificity Metric) slider for tomato is adjusted to yield a similar number of hits
as in *Arabidopsis thaliana*. 

![Compare specificity](images/compare_specificity_entry.png "Compare specificity entry") 

In the resulting page orthogroups with a member expressed in one, the other or both selected conditions are shown in a
venn diagram, with a detailed list below. By hovering over a gene, the description can be observed. 

![Compare specificity](images/compare_specificity_result.png "Compare specificity result") 

Here, the first reported hit is AGL1 aka. SHATTERPROOF 1, a known fruit development gene, clearly illustrating the power of this 
approach.

## Sub- or Neofunctionalization