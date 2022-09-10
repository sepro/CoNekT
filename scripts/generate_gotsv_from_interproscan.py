#!/usr/bin/env python

import argparse

version = 0.01
parser = argparse.ArgumentParser(description='Generates TSV file with GO per\
 gene from InterProScan results.', add_help=True)
parser.add_argument('-v', '--version', action='version', version=version)
parser.add_argument('--interproscan', '-i', dest='interproscan_file',
                    metavar='interproscan.tsv', type=str,
                    help='File with InterProScan results (TSV).',
                    required=True)
parser.add_argument('--tsv', '-o', dest='tsv_file',
                    metavar='go_tsv.tsv', type=str,
                    help='Output TSV (gene\tGO identifier\tevidence tag)).\
 (separated by tabulation)',
                    required=True)

args = parser.parse_args()
ipscan_f = args.interproscan_file
out_f = args.tsv_file

gene_gos = {}

ipscan_f_obj = open(ipscan_f, 'r')
for line in ipscan_f_obj:
    iprscan_fields = line.rstrip().split('\t')
    if len(iprscan_fields) > 13:
        if iprscan_fields[13].startswith('GO:'):
            #print(f'{iprscan_fields[0]}\t{iprscan_fields[13]}')
            go_list = iprscan_fields[13].split('|')
            for go_id in go_list:
                if iprscan_fields[0] in gene_gos.keys():
                    if go_id not in gene_gos[iprscan_fields[0]]:
                        gene_gos[iprscan_fields[0]].append(go_id)
                        #print(gene_gos[iprscan_fields[0]])
                else:
                    gene_gos[iprscan_fields[0]] = [go_id]
                    #print(gene_gos[iprscan_fields[0]])
                
ipscan_f_obj.close()

out_f_obj = open(out_f, 'w')

out_f_obj.write('gene_name\tGO\tevidence_tag\n')
for gene in gene_gos.keys():
    for go_id in gene_gos[gene]:
        out_f_obj.write(gene+"\t"+go_id+"\tISM\n")

out_f_obj.close()