# CARD k-mers
Fast, AMR-aware k-mer classification to predict **pathogen-of-origin** (species/genus) and **genomic context** (chromosome vs plasmid) for reads that encode antimicrobial resistance (ARG) genes.  

> Built to work hand-in-glove with the Comprehensive Antibiotic Resistance Database (CARD) and the Resistance Gene Identifier (RGI). 
> CARD : https://card.mcmaster.ca  
> RGI GitHub : https://github.com/arpcard/rgi

---

## Why CARD k-mers?

General k-mer taxonomic tools (e.g., Kraken2, CLARK) excel on broad sequence space but underperform on AMR-focused reads. CARD k-mers narrows the reference to **ARG alleles from CARD-R**, enabling:
- **Higher species-level accuracy** on pathogen-specific AMR alleles  
- **Low erroneous call rate** via a conservative decision logic  
- **Genomic context calls** (chromosome, plasmid, or both)  

---

## Citation

If you use CARD k-mers in a publication, please cite:  

> Wlodarski, M.A., T.T.Y. Lau, B.P. Alcock, A.R. Raphenya, T.E. Ta, F. Maguire, R.G. Beiko, & A.G. McArthur. CARD k-mers: Unmasking the pathogen hosts and genomic contexts of antimicrobial resistance genes in metagenomic sequences. Manuscript in preparation. 

Validation Data: [validation](/validation/)

Supplementary Figures: [supplementary](/supplementary/)

---

## Table of contents
- [Features](#features)
- [When to use](#when-to-use)  
- [Install](#install)  
- [Quickstart](#quickstart)  
- [End-to-end workflow](#end-to-end-workflow)  
- [Input types](#input-types)  
- [Outputs](#outputs)  
- [Interpreting output](#interpreting-output)  
- [Build a custom k-mer database](#build-a-custom-k-mer-database-optional)  

---

## Features
- **ARG-aware taxonomy**: species and genus predictions tailored to resistance gene space  
- **Genomic origin**: predicts chromosome vs plasmid context for mobility risk assessment  
- **Flexible input**: FASTA, RGI JSON (assemblies), RGI BAM (metagenomic reads)  
- **Outputs**: human-readable TXT summaries and structured JSON evidence files  
- **Validation data**: workflows and manifests included to reproduce published benchmarks  

---

## When to use
- You want to link detected **ARGs** to their most likely **pathogen host** and **genomic context**.  

> **Important**: CARD k-mers assumes inputs encode ARGs.  
> Run RGI (`rgi bwt`) first to filter reads for AMR reads.  : https://github.com/arpcard/rgi/blob/master/docs/rgi_bwt.rst  
> For non-AMR reads, use a general taxonomy tool.  

---

## End-to-end workflow
1. Download CARD data  
2. Load precompiled k-mers  
3. Run `rgi kmer_query` on inputs  
4. Summarize + visualize  

---

## Install

### Step 1 — Install RGI
https://github.com/arpcard/rgi  

### Step 2 — Load CARD data & precompiled k-mers

```bash
rgi clean --local

wget https://card.mcmaster.ca/latest/data -O card_data.tar
tar -xvf card_data.tar ./card.json

rgi load --card_json ./card.json --local

rgi card_annotation -i ./card.json > card_annotation.log 2>&1
rgi load -i ./card.json --card_annotation card_database_v3.0.1.fasta --local
```

```bash
wget -O wildcard_data.tar.bz2 https://card.mcmaster.ca/latest/variants
mkdir -p wildcard && tar -xjf wildcard_data.tar.bz2 -C wildcard
gunzip wildcard/*.gz

rgi load --card_json ./card.json   --kmer_database ./wildcard/61_kmer_db.json   --amr_kmers ./wildcard/all_amr_61mers.txt   --kmer_size 61 --local > kmer_load.61.log 2>&1
```

---
### Step 3 — Run RGI kmer_query

```bash
rgi kmer_query -h
```

```bash
usage: rgi kmer_query [-h] -i INPUT [--bwt] [--rgi] [--fasta] -k K [-m MIN]
                      [-n THREADS] -o OUTPUT [--local] [--debug]

Resistance Gene Identifier - 6.0.2 - Kmer Query

Tests sequenes using CARD*kmers

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file (bam file from RGI*BWT, json file of RGI results, fasta file of sequences)
  --bwt                 Specify if the input file for analysis is a bam file generated from RGI*BWT
  --rgi                 Specify if the input file is a RGI results json file
  --fasta               Specify if the input file is a fasta file of sequences
  -k K, --kmer_size K   length of k
  -m MIN, --minimum MIN
                        Minimum number of kmers in the called category for the classification to be made (default=10).
  -n THREADS, --threads THREADS
                        number of threads (CPUs) to use (default=1)
  -o OUTPUT, --output OUTPUT
                        Output file name.
  --local               use local database (default: uses database in executable directory)
  --debug               debug mode
```

---

## Quickstart

**RGI BWT BAM input (metagenomic reads, recommended)**  
```bash
rgi kmer_query --bwt --kmer_size 61 --threads 8 --minimum 10   --input data/sample/example_rgi_bwt.bam   --output results/example_bwt --local
```

**RGI JSON input (assemblies)**  
```bash
rgi kmer_query --rgi --kmer_size 61 --threads 8 --minimum 10   --input data/sample/example_rgi_main.json   --output results/example_rgi_main --local
```

**FASTA input (ARG sequences)**  
```bash
rgi kmer_query --fasta --kmer_size 61 --threads 8 --minimum 10   --input data/sample/example_reads.fasta   --output results/example_fasta --local
```

---

## Input types
- **FASTA**: ARG-containing reads or contigs, genomes
- **RGI JSON**: results from `rgi main` on assemblies  
- **RGI BWT BAM**: mapped metagenomic reads from `rgi bwt`  

---

## Outputs
- **TXT summaries**
- **JSON evidence files**

Both formats report:
- total k-mers per sequence  
- # of ARG k-mers  
- predicted pathogen (species/genus)  
- genomic context (chromosome/plasmid/both)  

---

### Step 4 — Summarize and interpret results

**TXT output (FASTA, Figure 2A)**  
Each row = one sequence.  
- `Sequence`: identifier from input FASTA  
- `Total # kmers`: all k-mers in sequence  
- `# of AMR kmers`: subset mapping to ARGs  
- `CARD k-mer prediction`: pathogen + genomic context (e.g., *E. coli (chromosome)*)  
- `Taxonomic kmers`: number of species/genus-specific k-mers matched  
- `Genomic kmers`: breakdown into plasmid, chromosome, or both  

**Example**:  
```
Sequence: J00138:91:HH7JKBXX
Total # kmers: 91
# of AMR kmers: 48
Prediction: Escherichia coli (chromosome)
Taxonomic kmers: Escherichia coli: 16
Genomic kmers: chr or pls: 0 | plasmid: 0 | chr: 5
```
<img width="1033" height="144" alt="Screenshot 2025-08-28 at 3 01 45 PM" src="https://github.com/user-attachments/assets/e26570a3-1cc7-4351-8baa-e5c803641400" />
Interpretation: This ARG read is predicted to originate from *Escherichia coli*, chromosome-borne.  

---

**JSON output (RGI BAM, Figure 2B)**  
Each read = one JSON object.  
- `reference`: ARG allele ID (ARO, name, NCBI accession)  
- `#_of_kmers_in_sequence` / `#_of_AMR_kmers`: counts  
- `taxonomic_info`: dictionary of species/genus with hit counts  
- `genomic_info`: dictionary of chr/pls/plasmid counts  

**Example**:
```json
"read_2": {
  "reference": "ARO:3002867|Name:dfrF|NCBI:AF028812.1",
  "#_of_kmers_in_sequence": 91,
  "#_of_AMR_kmers": 47,
  "taxonomic_info": {
    "species": { "Escherichia coli": 11 }
  },
  "genomic_info": {
    "chr or pls": 0,
    "plasmid": 5,
    "chr": 0
  }
}
```
<img width="1033" height="470" alt="Screenshot 2025-08-28 at 3 02 41 PM" src="https://github.com/user-attachments/assets/31c8b48c-5215-4093-a5b2-3926e511b894" />

---

## Build a custom k-mer database (optional)

CARD provides precompiled 61-mers, but you can also build custom k-mer sets at other sizes (e.g., 31-mers or 15-mers) using `rgi kmer_build`. This is useful if you want to explore accuracy vs. runtime trade-offs.

### Example: build k=31 with 20 threads
```bash
# Assumes CARD annotation FASTA and wildcard prevalence files exist
rgi kmer_build   --input_directory ./wildcard   --card card_database_v3.0.1.fasta   -k 31   --threads 20   --batch_size 100000
```

### Re-run with a different k without regenerating intermediates
```bash
rgi kmer_build   --input_directory ./wildcard   --card card_database_v3.0.1.fasta   -k 33   --threads 20   --batch_size 100000   --skip
```

### Load your custom database
```bash
rgi load --card_json ./card.json   --kmer_database ./wildcard/31_kmer_db.json   --amr_kmers    ./wildcard/all_amr_31mers.txt   --kmer_size 31   --local
```

**Tips**  
- Smaller k (e.g., 15) → faster queries, slightly less precise.  
- Larger k (e.g., 61) → higher precision, slower.  
- Adjust `--minimum` coverage threshold when using smaller k to avoid spurious hits.  

