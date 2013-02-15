#! /usr/bin/env python

import json
from argparse import ArgumentParser
from utils import *

def closest(v,l):
  "closet value to v in l"
  return min(l, key=lambda x: abs(x-v))

def project(masses, onto_masses):
  indexes, m = masslist_to_indexlist(masses)
  onto_indexes, onto_m = masslist_to_indexlist(onto_masses)
  assert m == onto_m
  return indexlist_to_masslist(
    sorted(set(closest(i,onto_indexes) for i in indexes)), m)

def project_items(items, onto):
  return { doc_id:{ c:project(l, onto[doc_id].values()[0]) 
                    for c,l in items[doc_id].items() }
           for doc_id in items }

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'segmentations', help='file with segmentations to be projected')
  p.add_argument(
    'boundaries', help='file with boundaries to be projected upon')
  return p.parse_args()

def main():
  args = parse_args()
  s = load_segmentation_data(args.segmentations)
  b = load_segmentation_data(args.boundaries)
  o = { 'id':'{}-projected-onto-{}'.format(s['id'],b['id']),
        'segmentation_type':'linear',
        'items': project_items(s['items'], b['items']) }
  print json.dumps(o, sort_keys=True)

if __name__ == "__main__":
  main()
