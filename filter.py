#! /usr/bin/env python

import json
from argparse import ArgumentParser
from utils import *

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    'coders', help='only include specified coders', action='append')
  return p.parse_args()

def main():
  "Filter a segmentation file to only include the specified coders."
  args = parse_args()
  o = load_segmentation_data(args.filename)
  filtered = {
    'segmentation_type': o['segmentation_type'],
    'id': '&'.join([ c.lower() for c in args.coders ]),
    'items': filter_coders(o['items'], args.coders) }
  print json.dumps(filtered, sort_keys=True)
  
if __name__ == "__main__":
  main()
