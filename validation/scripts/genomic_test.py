#analyze card k-mers txt fasta summary outputs for type test only
import json, csv
import argparse, os, random, sys
from Bio import SeqIO
import pandas as pd

#Help documentation
parser = argparse.ArgumentParser(description='analyze card kmers outputs')
parser.add_argument('-i', '--card_file', dest='card_index', type=str, default='', help='card-r index json')
parser.add_argument('-f', '--query_file', dest='query_file', type=str, default="", help='card kmers txt query results')
parser.add_argument('-k', '--ksize', dest='kmer_size', type=int, default=61, help='kmer size')
args = parser.parse_args()

#open card-r index as reference and query fasta summary
index = json.load(open(args.card_index))
query = csv.DictReader(open(args.query_file, "r"), delimiter="\t")

#keep metrics: bp =plasmid but labelled both, bc = chr but labelled both, p = plasmid, pt = plasmid_total, c = chromosome, ct = chromosome_total, ep = erroneous plasmid, ec = erroneous chromosome, a = ambiguous, r = rejected, t = total lines
bp, bc, p, pt, c, ct, ep, ec, ap, rp, ac, rc,  t = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0 

#iterate over query results
for entry in query:
    #increment total
    t += 1

    #scrape prevalence sequence id
    i,j = entry["Sequence"].index(":"), entry["Sequence"].index("|")
    prev_id = entry["Sequence"][i + 1 : j]

    prediction = entry["CARD*kmer Prediction"]
    
    #grade prediction
    if list(index[prev_id]["data_type"].keys())[0] == "ncbi_plasmid":
        pt += 1
        if prediction == "N/A":
            rp += 1
        elif prediction == "no genomic info" or prediction == "Unknown taxonomy and genomic context":
            ap += 1
        else:
            data_type = prediction[prediction.index("(") + 1 : prediction.index(")")]
            if "ncbi_" + data_type == "ncbi_plasmid":
                p += 1
            elif data_type == "chromosome or plasmid":
                bp += 1
            else:
                ep += 1
    elif list(index[prev_id]["data_type"].keys())[0] == "ncbi_chromosome":
        ct += 1
        if prediction == "N/A":
            rc += 1
        elif prediction == "no genomic info" or prediction == "Unknown taxonomy and genomic context":
            ac += 1
        else:
            data_type = prediction[prediction.index("(") + 1 : prediction.index(")")]
            if "ncbi_" + data_type == "ncbi_chromosome":
                c += 1
            elif data_type == "chromosome or plasmid":
                bc += 1
            else:
                ec += 1

print("plasmid stats: ", round(p / pt, 4), round(ep / pt, 4), round(bp / pt, 4), round(ap / pt, 4), round(rp / pt, 4))
print("chromosome stats: ", round(c / ct, 4), round(ec / ct, 4), round(bc / ct, 4), round(ac / ct, 4), round(rc / ct, 4))
print("plasmid totals: ", p, ep, bp, ap, rp)
print("chromosome totals: ", c, ec, bc, ac, rc)
