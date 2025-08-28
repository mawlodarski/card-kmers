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

See the [manuscript for methods and benchmarking results](https://github.com/wlodarsm/card_k-mers/tree/main).

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
- [Choosing k-mer size](#choosing-k-mer-size)  
- [Reproducing validation](#reproducing-validation)  
- [Performance notes](#performance-notes)  
- [Cite](#cite)  
- [License](#license)  
- [Contributing](#contributing)  

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
- You favor **precision over recall** (conservative assignments minimize false positives).  

> **Important**: CARD k-mers assumes inputs encode ARGs.  
> Run RGI (`rgi bwt`) first to filter for AMR reads.  
> For non-AMR reads, use a general taxonomy tool.  

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

## Quickstart: Classify

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

## End-to-end workflow
Scripts and Snakemake pipeline are included to automate:
1. Download CARD data  
2. Load precompiled k-mers  
3. Run `rgi kmer_query` on inputs  
4. Summarize + visualize  

---

## Input types
- **FASTA**: ARG-containing reads or contigs  
- **RGI JSON**: results from `rgi main` on assemblies  
- **RGI BWT BAM**: mapped metagenomic reads from `rgi bwt`  

---

## Outputs
- **TXT summaries** (for FASTA / RGI JSON inputs)  
- **JSON evidence files** (for BAM inputs)  

Both formats report:
- total k-mers per sequence  
- # of ARG k-mers  
- predicted pathogen (species/genus)  
- genomic context (chromosome/plasmid/both)  

---

## Interpreting output

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
<img width="1093" height="144" alt="Screenshot 2025-08-28 at 2 21 41 PM" src="https://github.com/user-attachments/assets/5e955efe-7661-4989-a85f-ca74be76a724" />

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
<img width="1093" height="489" alt="Screenshot 2025-08-28 at 2 21 25 PM" src="https://github.com/user-attachments/assets/0764aaf4-96b1-4229-9cb2-6e2e6738a814" />

Interpretation: This ARG read is predicted to originate from *Escherichia coli*, plasmid-borne.  

---

## Choosing k-mer size
- **61-mers (default)**: higher accuracy, slower queries  
- **15-mers**: faster builds, ~80% accuracy plateau  

---

## Reproducing validation
Validation manifests and notebooks are provided in `data/validation/` and `notebooks/`.  
They reproduce the pathogen/genomic benchmarks in the manuscript.  

---

## Performance notes
- Query speed scales with threads  
- Pre-filter reads with `rgi` for efficiency  
- Memory usage stable across thread counts  

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
