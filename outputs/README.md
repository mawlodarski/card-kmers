# CARD k-mers — final outputs by test

Final results backing the CARD k-mers manuscript (v10 revision). One folder per test.
Figures and the manuscript itself are submitted separately. File-by-file documentation
is in `DOCUMENTATION.md`; byte size, gzip size, md5 and original workspace path for
every file is in `MANIFEST.csv`.

| Folder | What it holds |
|---|---|
| `00_reference_inputs` | Two-thirds/one-third split FASTAs and the CARD-R truth maps every downstream test is scored against. |
| `01_allele_third_split` | The 103,389-allele held-out benchmark: raw output from all four classifiers, the per-allele scored table, and every metric table behind Figure 2 and Supplementary Figures 2–3. |
| `02_kmer_size_sweep` | k = 4–100 for taxonomy and genomic context, point estimates with 2,000-draw bootstrap intervals plus the full replicate files. |
| `03_genome_spikein` | Final CARD k-mers results for the 25 whole-genome spike-in libraries, plus the protein-homolog-model resistome of the four clinical isolates. |
| `04_allele_spikein` | Final CARD k-mers results for the allele-level spike-ins. |
| `05_sewage` | Final CARD k-mers results across the sewage metagenomes. |
| `06_other` | The unclassified-allele UMAP and its coordinates, the allele/pathogen distribution, and the computing-performance records. |

## Reproducing

Files over ~300 KB are gzip-compressed (`.gz`); `gunzip` before use. `.tar.gz` archives
and the UMAP `.html` are stored uncompressed/already-archived and can be opened directly.

1. `gunzip 00_reference_inputs/training.fasta.gz 00_reference_inputs/testing.fasta.gz` and
   build/query with `rgi kmer_build` / `rgi kmer_query` (see root [README](/README.md)).
2. Score outputs against ground truth with the scripts in [`/validation`](/validation/),
   using `00_reference_inputs/index-for-model-sequences-cardr-4.0.0.json.gz` as the index.
3. Compare against the pre-computed tables in `01_allele_third_split` onward — each
   folder's final result table is marked in `DOCUMENTATION.md`.
