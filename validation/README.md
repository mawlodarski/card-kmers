# Validation Data

This folder contains the curated **training and testing datasets** used to benchmark CARD k-mers against other classifiers (Kraken2, CLARK, KITSUNE) as described in the manuscript. These datasets ensure that validation can be reproduced exactly as reported.

---

## Files overview

- **`card-r.fasta`**  
  The complete **CARD-R allele reference set**.  
  - Basis for both training and testing splits.  
  - Contains all curated AMR alleles sampled across pathogens and plasmids.  

- **`training.fasta`**  
  The **custom training database** for k-mer methods.  
  - Used to build the CARD k-mers database.  
  - Also used as the AMR-restricted database for **Kraken2 (CARD)**.  
  - Represents ~two-thirds of the CARD-R alleles (training split).  

- **`testing.fasta`**  
  The **held-out validation sequences** for pathogen benchmarking.  
  - Used to test **CARD k-mers**, **Kraken2**, **Kraken2 (CARD)**, **CLARK**, and **KITSUNE pathogen classifiers**.  
  - Contains ~one-third of the CARD-R alleles (test split).  
  - Each sequence is labeled with the **ground-truth pathogen species/genus** for accuracy evaluation.  

- **`genomic.fasta`**  
  The **validation sequences for genomic context benchmarking**.  
  - Used to test **CARD k-mers genomic classifier** (chromosome vs plasmid vs both).  
  - Sequences are labeled with **genomic context ground truth**.  

- **`plasmid.fasta`**  
  Specialized validation set for the **KITSUNE k-mer size validation**.  

- **`index-for-model-sequences.json` (or equivalent manifest)**  
  Mapping file with **ground-truth labels** for all validation sequences.  

---

## Reproducing the manuscript tests

Follow these steps to recreate the benchmarking experiments exactly as described:

### 1. Build training/standard databases and classify `testing.fasta`
- **CARD k-mers**:  
  ```bash
  rgi kmer_build     --input_directory training.fasta     --card card-r.fasta     -k 61     --threads 20
  ```
- **Kraken2 (CARD)**: build Kraken2 database from `training.fasta`, classify `testing.fasta`
- **Kraken2**: build Kraken2 standard database, classify `testing.fasta`
- **CLARK**: build CLARK database, classify `testing.fasta`
- **KITSUNE**: build pathogen or plasmid k-mer CRE curves with KITSUNE

Compare predictions to **ground truth** in `index-for-model-sequences.json`.  

### 3. Run genomic validation
- Classify `genomic.fasta` with CARD k-mers genomic classifier.  
- Compare predicted **chromosome/plasmid/both** labels against genomic type ground truth labels in `index-for-model-sequences.json`.  

---

# Validation Scripts

This folder includes two Python scripts for scoring **CARD k-mers validation experiments** against the curated ground truth: one for **species/genus accuracy**, and one for **genomic context**.

---

## species_test.py — Pathogen-of-origin accuracy

Evaluates **CARD k-mers TXT (FASTA-mode) outputs** against the CARD-R index to measure:
- **correct species** rate  
- **correct genus (but wrong species)** rate  
- **erroneous** predictions (wrong genus)  
- **ambiguous** calls (`Unknown …`)  
- **rejected** calls (`N/A`)  

### Inputs
- `-i, --card_file` → CARD-R index JSON (species ground truth)  
- `-f, --query_file` → CARD k-mers TXT summary (from `rgi kmer_query --fasta …`)  

### Usage
```bash
python species_test.py   --card_file data/validation/card_r_index.json   --query_file results/example_fasta.txt
```

### Output
- Prints a one-line analysis summary to stdout, e.g.:  
  ```
  analysis summary:
   correct species: 0.8421 800 erroneous: 0.0532 50 correct genus: 0.0716 68 ambiguous: 0.0200 19 rejected: 0.0132 12
  ```

---

## genomic_test.py — Genomic context accuracy

Evaluates **CARD k-mers TXT (FASTA-mode) outputs** for genomic origin: **chromosome vs plasmid vs both**.  

Metrics include:
- **chromosome correct** rate  
- **chromosome misclassified as both**  
- **chromosome erroneous**  
- **chromosome ambiguous/rejected**  
- **plasmid correct** rate  
- **plasmid misclassified as both**  
- **plasmid erroneous**  
- **plasmid ambiguous/rejected**  

### Inputs
- `-i, --card_file` → CARD-R index JSON (genomic context ground truth)  
- `-f, --query_file` → CARD k-mers TXT summary (from `rgi kmer_query --fasta …`)  

### Usage
```bash
python genomic_test.py   --card_file data/validation/card_r_index.json   --query_file results/example_fasta.txt   --ksize 61
```

## Notes
- Both scripts expect **query TXT outputs** from FASTA-mode `rgi kmer_query`.  
- These scripts allow quick reproduction of the **accuracy tables** reported in the manuscript.  

## Notes

- Ground-truth labels are derived from CARD curation of **Resistomes & Variants** and **Prevalence data**.  
- Use the **same k-mer sizes** reported in the manuscript (CARD k-mers: 61 bp) to replicate results.  
- For reproducibility, always record:  
  - CARD data version  
  - RGI version  
  - Tool versions (Kraken2, CLARK, KITSUNE)  
  - k-mer size used  

---
