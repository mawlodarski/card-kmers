# CARD k-mers
Fast, AMR-aware k-mer classification to predict **pathogen-of-origin** (species/genus) and **genomic context** (chromosome vs plasmid) for reads that encode antimicrobial resistance (ARG) genes. 

> Built to work hand-in-glove with the Comprehensive Antibiotic Resistance Database (CARD) and the Resistance Gene Identifier (RGI). Implements the `rgi kmer_query` workflow and ships reproducible validation pipelines and visualizations.  
> CARD : https://card.mcmaster.ca  
> CARD GitHub : https://github.com/arpcard  

---

## Why CARD k-mers?

General k-mer taxonomic tools (e.g., Kraken2, CLARK) excel on broad sequence space but underperform on AMR-focused reads. CARD k-mers narrows the reference to **ARG alleles from CARD-R**, enabling:
- **Higher species-level accuracy** on pathogen-specific AMR alleles
- **Low erroneous call rate** via a conservative decision logic
- **Genomic context calls** (chromosome, plasmid, or both)

See the paper for methods, validation design, and results.

---

## Table of contents
- [Features](#features)
- [When to use](#when-to-use)
- [Install](#install)
- [Quickstart](#quickstart)
- [End-to-end workflow](#end-to-end-workflow)
- [Input types](#input-types)
- [Outputs](#outputs)
- [Choosing k-mer size](#choosing-k-mer-size)
- [Reproducing validation](#reproducing-validation)
- [Visualization](#visualization)
- [Performance notes](#performance-notes)
- [Cite](#cite)
- [License](#license)
- [Contributing](#contributing)

---

## Features
- **ARG-aware taxonomy**: species and genus predictions tailored to resistance gene sequence space  
- **Genomic origin**: predicts chromosome vs plasmid (or both) for contextual AMR risk  
- **Multi-format input**: FASTA, RGI JSON (assemblies), RGI BAM (metagenomic reads)  
- **Outputs**: human-readable summaries plus JSON with counts per taxon/context  
- **Validation Data**: Data and workflow to reproduce manuscript results

---

## When to use
- You need **pathogen-of-origin** (species/genus) and **genomic context** of ARGs from short reads.
- You favor **low false positives** over forced assignments.

> **Assumption**: Inputs encode AMR genes (the k-mer reference is AMR-specific).
> Run RGI bwt module first to align reads to CARD's protein homolog models : https://github.com/arpcard/rgi/blob/master/docs/rgi_bwt.rst  
>  For non-AMR reads, run a general taxonomy classifier first.

---

## Install

###  STEP 1 - Install RGI
https://github.com/arpcard/rgi/tree/master

## Quickstart

###  STEP 2 - Load CARD data + k-mers
1) **Fetch CARD data**
```bash
rgi clean --local

wget https://card.mcmaster.ca/latest/data -O card_data.tar
tar -xvf card_data.tar ./card.json

rgi load --card_json ./card.json --local

rgi card_annotation -i ./card.json > card_annotation.log 2>&1
rgi load -i ./card.json --card_annotation card_database_v3.0.1.fasta --local
```

2) **Download precompiled k-mers & load**
```bash
wget -O wildcard_data.tar.bz2 https://card.mcmaster.ca/latest/variants
mkdir -p wildcard && tar -xjf wildcard_data.tar.bz2 -C wildcard
gunzip wildcard/*.gz

rgi load --card_json ./card.json   --kmer_database ./wildcard/61_kmer_db.json   --amr_kmers ./wildcard/all_amr_61mers.txt   --kmer_size 61   --local > kmer_load.61.log 2>&1
```

3) **Classify**
bash
-
RGI BWT BAM input (metagenomic reads, recommended)
```
rgi kmer_query --bwt --kmer_size 61 --threads 8 --minimum 10 \
  --input data/sample/example_rgi_bwt.bam \
  --output results/example_bwt --local
```
RGI JSON input
```
rgi kmer_query --rgi --kmer_size 61 --threads 8 --minimum 10 \
  --input data/sample/example_rgi_main.json \
  --output results/example_rgi_main --local
```
FASTA input
```
rgi kmer_query --fasta --kmer_size 61 --threads 8 --minimum 10 \
  --input data/sample/example_reads.fasta \
  --output results/example_fasta 
```

---

## End-to-end workflow

Scripts and Snakemake pipeline included.

---

## Input types

- FASTA
- RGI JSON
- RGI BWT BAM

---

## Outputs

- TXT summaries
- JSON files

---

## Choosing k-mer size

- **61-mers** (default): higher accuracy  
- **15-mers**: faster but slightly lower accuracy

---

## Reproducing validation

Validation manifests and notebooks included under `data/validation/` and `notebooks/`.

---

## Visualization

- Sunburst plots  
- Stacked bar accuracy plots  

---

## Performance notes

- Speeds scale with threads and k-mer size  
- Pre-filter inputs with RGI for efficiency  

---

## Cite

If you use CARD k-mers in a publication, please cite:

> Wlodarski, M.A. *et al.* “CARD k-mers: Unmasking the Pathogen Hosts and Genomic Contexts of Antimicrobial Resistance Genes in Metagenomic Sequences.”

---

## License

Apache-2.0

---

## Contributing

Please read `CODE_OF_CONDUCT.md` and `CONTRIBUTING.md`.
