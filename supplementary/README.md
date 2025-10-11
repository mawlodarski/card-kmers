# UMAP of Unclassified AMR Alleles

This folder contains the **UMAP analysis** used in the manuscript to explore **unclassified AMR alleles** (i.e. alleles with no confident CARD k-mer assignment).

## Files
- **`alleles_species_counts.csv`** — table of each ARG allele in CARD-R and the number of pathogens associated with it  
- **`unclassified_table.csv`** — input table of unclassified alleles  
  Columns:  
  - `species`: known host species  
  - `card_short_name`: ARG identifier  
  - `count`: number of unclassified reads/alleles  
  - `gene_list`: ARGs observed in context  

- **`umap.py`** — script to project the above into 2D with UMAP.  
- **`umap_unclassified.html`** — interactive visualization (open in a browser).
