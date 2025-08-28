#analyze card k-mers txt fasta summary outputs
import json, csv
import argparse, os, random, sys
from Bio import SeqIO
import pandas as pd

#Help documentation
parser = argparse.ArgumentParser(description='analyze card kmers outputs')
parser.add_argument('-i', '--card_file', dest='card_index', type=str, default='', help='card-r index json')
parser.add_argument('-f', '--query_file', dest='query_file', type=str, default="", help='card kmers txt query results')
args = parser.parse_args()

#open card-r index as reference and query fasta summary
index = json.load(open(args.card_index))
query = csv.DictReader(open(args.query_file, "r"), delimiter="\t")

#keep metrics: s = correct species, g = correct genus, e = erroneous, a = ambiguous, r = rejected, t = total lines
s, g, e, a, r, t, = 0, 0, 0, 0, 0, 0

#iterate over query results
for entry in query:
    #scrape prevalence sequence id
    i,j = entry["Sequence"].index(":"), entry["Sequence"].index("|")
    prev_id = entry["Sequence"][i + 1 : j]

    #if list(index[prev_id]["species_name"].keys())[0] not in ["Escherichia coli", "Klebsiella pneumoniae"]: #exclusion species
    #increment total
    t += 1

    prediction = entry["CARD*kmer Prediction"]
    
    #grade prediction
    if prediction == "N/A":
        r += 1
    elif prediction[:7] == "Unknown":
        a += 1
    else:
        species = prediction[:prediction.index("(") - 1]
        genus = species.split(" ")[0]
    
        if species == list(index[prev_id]["species_name"].keys())[0]:
            s += 1
        elif list(index[prev_id]["species_name"].keys())[0][:list(index[prev_id]["species_name"].keys())[0].index(" ")] == genus and species != list(index[prev_id]["species_name"].keys())[0] :
            g += 1
        else:
            e += 1
        
    #grade data type


print("analysis summary:\n", "correct species: ", round(s / t, 4), s, "erroneous: ", round(e / t, 4), e, "correct genus: ", round(g / t, 4), g, "ambiguous: ", round(a / t, 4), a,  "rejected: ", round(r / t, 4), r)
    
