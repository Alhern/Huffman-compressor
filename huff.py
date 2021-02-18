#! /usr/bin/env python
# -*- coding: utf-8 -*-


from sys import argv
from cStringIO import StringIO
import os
from bitarray import bitarray
import pickle

### GLOBAL VARIABLES ###

prefix = {}
bit_p = {}

#################################
########## COMPRESSION ##########
#################################

def leafp(x) : return isinstance(x[1], str)

def make_codes(node, code = '') :
    if leafp(node) : prefix[node[1]] = code
    else :
        make_codes(node[1], code + '0')
        make_codes(node[2], code + '1')

def compress_all(files, amount_files):
    comp_filename = 'archive.HUFF'
    occurrences = {}
    all_code_map = encode_all(files)
    with open(comp_filename, 'wb') as bin_file:
        pickle.dump(amount_files, bin_file, protocol=pickle.HIGHEST_PROTOCOL) # on sauvegarde le nombre de fichiers compressés dans le header pour pouvoir les décompresser plus tard
        pickle.dump(all_code_map, bin_file, protocol=pickle.HIGHEST_PROTOCOL)
        for i in files:
            with open(i, 'r') as f:
                text = f.read()
                for x in text:
                    occurrences[x] = occurrences.get(x, 0) + 1
                H = list(zip(occurrences.values(), occurrences.keys()))
                while H[1:]:
                    left = min(H) ; H.remove(left)
                    right = min(H) ; H.remove(right)
                    H.append((left[0] + right[0], left, right))
                H = H[0]
                make_codes(H)
                code_map = dict(zip(all_code_map.values(), all_code_map.keys()))
                bit_p = dict([(y, bitarray(x)) for x, y in code_map.iteritems()])
                huff = bitarray()
                huff.encode(bit_p, text)
                pickle.dump(huff, bin_file, protocol=pickle.HIGHEST_PROTOCOL)
    print("YOUR COMPRESSED FILE: %s" % comp_filename)



###################################
########## DECOMPRESSION ##########
###################################

# This of course works with only one compressed file. 

def decompress_all(filename):
    with open(filename, 'rb') as f:
        num_files = pickle.load(f)
        header = pickle.load(f)
        print("DECOMPRESSING......")
        for i in range(0, num_files):
            decomp_filename = filename.split('.')[0] + '_decompressed_' + str(i + 1) + '.txt'
            data = pickle.load(f)
            with open(decomp_filename, 'w') as decomp:
                decomp.write(''.join(data.decode(header)))
            print(decomp_filename)
    print("Done!")


##############################
##### ENCODING ALL FILES #####
##############################

def encode_all_aux(file):
    occurrences = {}
    text = file.read()
    for x in text:
        occurrences[x] = occurrences.get(x, 0) + 1
    H = list(zip(occurrences.values(), occurrences.keys()))
    while H[1:]:
        left = min(H) ; H.remove(left)
        right = min(H); H.remove(right)
        H.append((left[0] + right[0], left, right))
    H = H[0]
    make_codes(H)
    all_code_map = dict(zip(prefix.values(), prefix.keys()))
    all_bit_p = dict([(y, bitarray(x)) for x, y in all_code_map.iteritems()])
    return all_bit_p


def encode_all(files):
    all = StringIO()
    for f in files:
        with open(f, 'r') as file:
            all.write(file.read())
            all.write('\n')
    all.seek(0)
    complete_map = encode_all_aux(all)
    return complete_map


###################################
########## MAIN PROGRAM ###########
###################################

def usage():
    print("\n\t+-----------------------------------+")
    print("\t|              HUFFMAN              |")
    print("\t| COMPRESSION/DECOMPRESSION PROGRAM |")
    print("\t+-----------------------------------+\n")
    print("\tAdd 1 or more files, they will be compressed into 1 .HUFF archive.\n")
    exit("\tOptions:\n\t-c to compress\n\t-d to decompress\n\n\tUsage:\n\t ./ds03.5.py [-c|-d] [file]...\n")


def main():
    if (len(argv) <= 2):
        usage()
    files = []
    if (argv[1] == "-c"):
        try:
            for i in range(2, len(argv)):
                files.append(argv[i])
            amount_files = len(files)
            print("Compressing %i file(s)..." % amount_files)
            compress_all(files, amount_files)
        except:
            exit("File(s) unavailable")
    elif (argv[1] == "-d"):
        try:
            decompress_all(argv[2])
        except:
            exit("Archive unavailable")
    else:
        usage()


if __name__ == "__main__": main()
