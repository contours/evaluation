#! /usr/bin/env python

import json
from argparse import ArgumentParser
from utils import *

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument('filename', help='name of the JSON segmentation file')
  return p.parse_args()

def main():
  "Produce a null (no boundaries) segmentation for comparison purposes."
  args = parse_args()
  o = load_segmentation_data(args.filename)
  items =  { d:{ 'null':list(set([ sum(m) for m in s.values() ])) }
             for d,s in o['items'].items() }
  assert all(len(v['null']) == 1 for v in items.values())
  null = {
    'segmentation_type': 'linear',
    'id': 'null',
    'items': items }
  print json.dumps(null, sort_keys=True)
  
if __name__ == "__main__":
  main()
