#! /usr/bin/env python

import json, csv, os, sys

BASEDIR = os.path.dirname(os.path.realpath(__file__))

# Load the cellular component dictionary for distant supervision
isCC = {}
with open (BASEDIR + "/../data/training/is_cc.csv") as csvfile:
  reader = csv.reader(csvfile)
  for line in reader:
    term = line[0].strip()
    value = line[1].strip()
    if value == '1' or value=='true':
        isCC[term] = True
    elif value=='0' or value=='false':
        isCC[term] = False


# run through 
for row in sys.stdin:
    term = json.loads(row)['text']
    is_true = None
    if isCC.has_key(term):
        is_true = isCC[term]
        sys.stderr.write('found term: '+term+' value:'+str(is_true)+"\n")
    print(json.dumps({
          "term": term,
          "is_true": is_true,
          "relation_id": None
        }))






