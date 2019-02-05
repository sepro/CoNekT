# CRUD interface for tables

A few tables can be edited manually from the admin panel. This allows **News** items
to be posted, **species** to be edited (e.g. change color, add description). Furthermore,
names of **methods** (which appear on the website) can be altered or corrected when required.

## Condition Tissue table

One feature that can be enabled only through the CRUD interface is the comparative heatmap and heatmaps in phylogenetic trees. In the Condition Tissue table, set the field **in_tree** to true for tissues you want to compare. Note that this will **only** work for broad categories defined through the **Tissue Specificity** section (and will result in errors when **Condition Specificity** is used).
