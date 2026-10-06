# CARD k-mers — final outputs: file-by-file documentation

Companion to `MANIFEST.csv`, which carries the exact byte size, gzip size, md5 and
original workspace path of every file. Sizes below are raw MB. Figures and manuscript
documentation are **not** included here; they are submitted separately.

> **As stored in this repo:** files referenced below by their raw name (e.g.
> `training.fasta`) are compressed with a `.gz` suffix (e.g. `training.fasta.gz`) when
> over ~300 KB — see `README.md` in this folder. `master_genomes_phm_args.csv`, listed
> under `03_genome_spikein` below, was dropped as a confirmed exact duplicate of
> `master_phm_args.csv` before this deposit was added to the repo.

Common conventions across all result tables:

- **Outcome categories** are mutually exclusive and sum to the denominator:
  `correct_species` · `genus_only` (correct genus, no species named) ·
  `wrong_species_right_genus` (correct genus, wrong species named) ·
  `erroneous` (wrong genus) · `unclassified` · `rejected` (CARD k-mers only, query
  below the `--minimum` k-mer threshold).
- **Genomic context** categories: `chromosome` · `plasmid` · `chr + plasmid`
  (the allele is documented on both in CARD-R) · `unclassified` · `rejected`.
- **Intervals** are 95% percentile intervals from a 2,000-draw bootstrap, coupled across
  tools. Columns suffixed `_lo` / `_hi` are the bounds of the value in the unsuffixed
  column. Micro statistics resample all alleles; macro statistics resample within taxon.
- **Multi-value fields** (`drug_class`, `resistance_mechanism`, `amr_gene_family`) are
  `;`-separated in CARD. Tables named `*_by_drugclass` / `*_by_mechanism` are exploded,
  one row per value, so their row counts exceed the number of ARGs.

---

## 00_reference_inputs — 8 files, 1,519.4 MB

Inputs shared by every downstream test. All are derived from CARD Resistomes & Variants
v4.0.0 and are therefore subject to CARD's licence terms.

| File | MB | What it is |
|---|---:|---|
| `index-for-model-sequences-cardr-4.0.0.json` | 533.9 | The CARD-R master index. One record per prevalence sequence observation: prevalence ID, model ID, ARO term and accession, detection model, species, NCBI accession, data type (`ncbi_chromosome` / `ncbi_plasmid` / `ncbi_contig` / `ncbi_gi`), RGI criteria, identity, bitscore, gene family, mechanism, drug class, short name. Every truth label in this deposit traces back to this file. |
| `training.fasta` | 331.9 | Two-thirds reference split: 207,589 records collapsing to **207,450 unique** prevalence IDs. Used to build the 61-mer library and the Kraken2 CARD database. |
| `testing.fasta` | 164.8 | One-third held-out split: 103,456 records collapsing to **103,389 unique** prevalence IDs. The denominator for every allele-level result. |
| `formatted_training.fasta` | 314.4 | `training.fasta` rewritten with Kraken2 headers, `>id:N\|kraken:taxid\|TAXID species`. This is what Kraken2 actually consumed when building the CARD database. |
| `formatted_testing.fasta` | 156.0 | `testing.fasta` with the same header rewrite; the Kraken2 query input. Already deduplicated to 103,389 records. |
| `id_pathogen_map.json` | 12.8 | Prevalence ID → pathogen. The taxonomic ground truth. Values are a string (one pathogen) or a list (multi-pathogen alleles, excluded upstream). |
| `genomic_type_id_map.json` | 0.44 | Genomic-context ground truth. **Note the orientation:** two keys, `chromosome` and `plasmid`, each holding a list of prevalence IDs — not ID → context. The lists are disjoint. |
| `allele_species_counts.csv` | 5.2 | 320,614 rows. `Prevalence Sequence ID, CARD Short Name, species_count`. How many distinct pathogens encode each allele; underlies Supplementary Figure 5. |

## 01_allele_third_split — 28 files, 236.0 MB

The 103,389-allele held-out benchmark: CARD k-mers vs Kraken2 (default), Kraken2 (CARD)
and CLARK. Supports Figure 2 and Supplementary Figures 2 and 3.

### Raw classifier output

| File | MB | What it is |
|---|---:|---|
| `61mer_analysis.txt` | 19.3 | **Final CARD k-mers result.** One row per queried allele: total k-mers, AMR k-mers, taxonomic prediction with genomic-context qualifier in parentheses. |
| `testing_61mer_analysis.json` | 27.8 | The same run in JSON: per-allele k-mer counts broken down by species, genus and genomic class, without the collapsed call. |
| `kraken_default_out` | 71.2 | Kraken2 standard-database output, one row per query. |
| `kraken_custom_out` | 53.7 | Kraken2 CARD-database output. |
| `testing_clark_default.csv` | 10.2 | CLARK output. 103,456 rows; `Object_ID, Length, Assignment, Scientific_Name`. `NA`/`Error` in 34.07% of rows is CLARK declining to assign, not a mapping failure. |
| `kraken_results_default.json` | 13.7 | Per-allele Kraken2 default result joined to truth: species, predicted, match boolean. |
| `kraken_results_custom.json` | 13.6 | The same for the CARD database. |

### Taxonomy standardisation

Kraken2 returns NCBI taxonomy identifiers at any rank; these files are what converts them
to scientific names for scoring.

| File | MB | What it is |
|---|---:|---|
| `kraken_default_id_map.json` | 0.08 | taxid → scientific name, built from the Kraken2 run's own report. 1,706 entries. Identifiers `0` and `1` map to `unclassified`. |
| `kraken_custom_id_map.json` | 0.01 | The same for the CARD database. 350 entries. |
| `default_tax_report.txt` | 3.88 | The Kraken2 taxonomy report the default map was derived from. |
| `custom_tax_report.txt` | 3.84 | The same for the CARD database. |

### Scored per-allele tables

| File | Rows | What it is |
|---|---:|---|
| `per_allele_calls.tsv` | 103,389 | **The foundation table.** One row per allele: `prevalence_id, true_species, true_genus`, then prediction and outcome category for each of the four tools. Every metric in this folder is an aggregation of this file. |
| `per_allele_context.tsv` | 8,207 | One row per single-context allele: `prevalence_id, tool, true_context, predicted_context`. CARD k-mers only — no other tool predicts genomic context. |

### Metrics

| File | Rows | What it is |
|---|---:|---|
| `figure1_classifier_metrics.csv` | 4 | One row per tool, 117 columns: outcome counts, TP/FP/FN, species and genus precision/recall/F1 under both FP conventions, micro and macro, each with bootstrap bounds, plus `ck_minus_*` paired differences against CARD k-mers with significance flags. |
| `figure1_tidy.csv` | 56 | The same in long form — `tool, level, averaging, metric, value, ci_lo, ci_hi` — for plotting. |
| `figure1_outcomes.csv` | 24 | Outcome counts and percentages per tool, with stack order for bar charts. |
| `figure1_by_species.csv` | 1,260 | 315 species × 4 tools: support, TP/FP/FN, precision/recall/F1 per species. |
| `figure1_pairwise.csv` | 36 | Coupled paired differences: `comparison, metric, diff_pp, diff_lo, diff_hi, significant, favours`. Because draws are coupled, this is the correct test for "does A beat B", not overlapping marginal intervals. |
| `by_pathogen_bootstrap.csv` | 1,260 | As `figure1_by_species` but with bootstrap intervals, resampled within pathogen, and a support tier label. |
| `context_outcomes.csv` | 10 | Genomic-context confusion: 2 true contexts × 5 predicted categories, with row-wise (`pct_of_true`) and column-wise (`pct_of_predicted`) normalisation and bounds. |
| `context_prf.csv` | 8 | Genomic-context precision/recall/F1 per class plus micro and macro, under two conventions: `resolved` (a dual-context call is an abstention) and `inclusive` (credited to the true class, charged as FP to the other). |
| `context_tidy.csv` | 24 | `context_prf` in long form for plotting. |
| `stats_ci_mcnemar.tsv` | 28 | Wilson score intervals and McNemar paired tests — the analytic counterpart to the bootstrap. |
| `rescore_final.tsv` | 4 | Compact per-tool outcome summary with the common 103,389 denominator. |
| `supp_by_pathogen_context.csv` | 635 | Supplementary Figure 2 data: pathogen × genomic type, with recall, precision and unclassified rate. Point estimates, not bootstrap means; `n` is the allele count in that cell. |
| `supp_by_mechanism_context.csv` | 17 | Supplementary Figure 3A: resistance mechanism × genomic type. |
| `supp_by_drugclass_context.csv` | 96 | Supplementary Figure 3B: drug class × genomic type. |
| `supp_by_genefamily_context.csv` | 438 | The same by AMR gene family. |

## 02_kmer_size_sweep — 4 files, 59.5 MB

k = 4 to 100, on the same library and held-out set as the primary benchmark; k=61
reproduces the primary tables exactly. Supports Figure 3A and 3B.

| File | Rows | What it is |
|---|---:|---|
| `ksweep_bootstrap.csv` | 97 | One row per k. Outcome counts, then species and genus precision/recall/F1, call rate and abstention, each with bootstrap bounds. |
| `ksweep_bootstrap_draws.csv` | 194,000 | Every replicate behind those intervals: one row per k × draw (97 × 2,000), with the six counts, their percentages, and the eight per-draw metrics. |
| `context_sweep.csv` | 970 | Genomic context per k: 97 k × 2 true contexts × 5 predicted categories. |
| `context_sweep_draws.csv` | 194,000 | The replicate file for the context sweep. **Column names embed the category label**, e.g. `chromosome__chr + plasmid` — valid CSV, but needs backticks in R. |

## 03_genome_spikein — 8 files, 3.8 MB

Four clinical isolates spiked into a depleted 3,000,000-pair sewage background at five
coverages, plus a four-species mixture. Supports Figure 4 and Supplementary Figure 7.

| File | Rows | What it is |
|---|---:|---|
| `master_kmer_spikein_results.csv` | 1,188 | **Final CARD k-mers result.** One row per species × coverage × ARO: mapped reads with k-mer support, the prediction string, and read counts split across single-species / single-genus / unknown-taxonomy × genomic context. `species` = `mixed` for the four-species libraries. |
| `spikein_per_library_kmer_results.tar.gz` | 75 files | Per-library CARD k-mers output (gene- and allele-level) for all 25 libraries, before aggregation into the master. |
| `master_phm_args.csv` | 155 | Protein-homolog-model resistome of the four isolates: one row per ARG with gene, ARO, cut-off, identity, % reference length, bitscore, `arg_length_bp`, contig coordinates, drug class, mechanism, gene family. `arg_length_bp` is what the spike-in ARG burden was computed from. |
| `master_genomes_phm_args.csv` | 155 | A second copy of the same table from a separate build. **Diff these and keep one before deposit.** |
| `master_phm_args_by_drugclass.csv` | 473 | The above exploded by drug class. |
| `master_phm_args_by_mechanism.csv` | 164 | Exploded by resistance mechanism. |
| `rgi_main_summary.csv` | 8 | One row per genome per RGI run (all models vs homolog only): hit counts, Perfect/Strict/Loose, per-model-type counts, distinct families/classes/mechanisms, identity and length statistics. |
| `rgi_main_by_model.csv` | 16 | Model-type breakdown in long form. |

## 04_allele_spikein — 3 files, 28.0 MB

1,000 alleles simulated individually into the same background at five coverages ×
10 replicates. Supports Figure 5 and Supplementary Figure 8.

| File | Rows | What it is |
|---|---:|---|
| `simulomes_kmer_gene_master_annotated.csv` | 64,583 | **Final CARD k-mers result.** One row per replicate set × allele × coverage × ARO, with the same read-count breakdown as the genome spike-in master, plus annotation columns. |
| `simulomes_kmer_gene_master.csv` | 59,276 | The unannotated version. |
| `simulome_read_pairs.csv` | 50,000 | Simulated read pairs per condition: `Simulome_Set, Allele, Prevalence_Sequence_ID, ARO, Coverage, Read_Pairs`. 1,000 alleles × 5 coverages × 10 replicates. |

## 05_sewage — 2 files, 31.7 MB

Global Sewage Surveillance metagenomes screened with RGI bwt and classified with CARD
k-mers. Supports Figure 6.

| File | Rows | What it is |
|---|---:|---|
| `master_kmer_sewage_results.csv` | 76,352 | **Final CARD k-mers result.** One row per sample × ARO, with country and continent, mapped reads with k-mer support, prediction string, and the taxonomy × genomic-context read breakdown. Covers **237 samples**. |
| `sewage_per_sample_kmer_results.tar.gz` | 498 files | Per-sample gene- and allele-level CARD k-mers output for **249 samples**. The twelve samples present here but absent from the master produced output with no rows in the aggregate — reconcile before publication, since the manuscript states 249. |

Raw reads are public (Hendriksen et al. 2019) and the 500 GB of RGI bwt BAMs are not
deposited; both are regenerable from ENA accessions.

## 06_other — 10 files, 4.8 MB

| File | What it is |
|---|---|
| `unclassified_umap_k61.html` | Supplementary Figure 6. Interactive 3D UMAP of the 20,936 alleles CARD k-mers left unclassified at k=61, embedded as 3,556 (gene, pathogen) points under the Jaccard metric. Hover shows species, gene and count; no printed labels. |
| `unclassified_umap_k61_coords.csv` | The 3,556 points with coordinates: `card_short_term, species, count, umap_x, umap_y, umap_z, newcount`. Lets the figure be rebuilt or re-styled without re-running UMAP. |
| `supp_fig4_allele_pathogen_distribution.csv` | 58 rows, `n_pathogens, n_alleles`. The distribution behind Supplementary Figure 5: 310,892 alleles in one pathogen, 9,722 in more than one, maximum 96. |
| `1mill_time_query_{15,61}mer_{1,40}thread` | GNU `time -v` records for `rgi kmer_query` over 1,000,000 reads. Wall clock: 15-mer 4:44.52 (1 thread) / 1:29.06 (40); 61-mer 4:54.46 / 2:19.46. These give 210,881 / **673,703** / 203,763 / 430,231 reads per minute. The manuscript's "approximately 675,000" is the 15-mer 40-thread figure. |
| `time_library_build_{15mer_1thread,15mer_40thread,61mer_40thread}` | `time -v` records for `rgi kmer_build`. **`time_library_build_61mer_1thread` is absent** from the source: that file holds build log output rather than a timing record, so there is no wall-clock figure for the 61-mer single-threaded build. |

---

## Known issues carried into this deposit

1. ~~`master_phm_args.csv` and `master_genomes_phm_args.csv` are both 42,108 bytes and
   almost certainly identical; keep one.~~ **Resolved** — confirmed byte-identical
   (md5 `f9bd7943c015b3d948fe8790c5e1b3f9`) and the duplicate removed; see this folder's
   `README.md`.
2. The sewage master covers 237 samples against 249 per-sample result sets and a
   manuscript figure of 249. **Open** — see this folder's `README.md`.
3. No wall-clock record exists for the 61-mer single-threaded library build. **Open.**
4. All of `00_reference_inputs` is CARD-R derived and subject to CARD's licence, which
   restricts reproduction by commercial organisations without written McMaster
   permission. Non-commercial/academic use is permitted; see this folder's `README.md`.
