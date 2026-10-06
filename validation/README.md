# Validation

This folder holds the reusable scoring scripts for CARD k-mers validation. The
underlying datasets previously stored here (training/testing FASTAs, the CARD-R index,
and the earlier KITSUNE-era genomic/plasmid validation sets) have been superseded by
the complete, versioned final-results deposit in **[`/outputs`](/outputs/)**, which backs
the current manuscript (v10 revision) and additionally covers the k-mer size sweep,
genome/allele spike-ins, and sewage surveillance tests that this folder predates.

- Training/testing splits + CARD-R ground truth → [`/outputs/00_reference_inputs`](/outputs/00_reference_inputs/)
- Per-allele classifier outputs and scored benchmark tables → [`/outputs/01_allele_third_split`](/outputs/01_allele_third_split/)

KITSUNE is no longer part of the tool comparison in the current manuscript (only CARD
k-mers, Kraken2 default, Kraken2 (CARD), and CLARK), so the standalone genomic/plasmid
validation FASTAs built for it were retired rather than carried forward; genomic-context
scoring is now done via `per_allele_context.tsv` in `01_allele_third_split`.

---

# Validation Scripts

Two Python scripts for scoring **CARD k-mers validation experiments** against curated
ground truth: one for **species/genus accuracy**, and one for **genomic context**. Both
expect query TXT outputs from FASTA-mode `rgi kmer_query` and a CARD-R index JSON — use
`/outputs/00_reference_inputs/index-for-model-sequences-cardr-4.0.0.json.gz` (gunzipped)
as the index.

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
python species_test.py --card_file index-for-model-sequences-cardr-4.0.0.json --query_file results/example_fasta.txt
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
python genomic_test.py --card_file index-for-model-sequences-cardr-4.0.0.json --query_file results/example_fasta.txt --ksize 61
```

## Notes
- Both scripts expect **query TXT outputs** from FASTA-mode `rgi kmer_query`.  
- Ground-truth labels are derived from CARD curation of **Resistomes & Variants** and **Prevalence data**.  
- Use the **same k-mer sizes** reported in the manuscript (CARD k-mers: 61 bp) to replicate results.  
- For reproducibility, always record: CARD data version, RGI version, tool versions (Kraken2, CLARK), k-mer size used.

---
