#! /usr/bin/env python

import json
from argparse import ArgumentParser
from itertools import ifilterfalse
from random import random
from utils import *

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument('filename', help='name of the JSON segmentation file')
  return p.parse_args()

def proportion_of_boundaries(items):
  index_lists, m = masses_to_indexes(overall_segmentations(items))
  boundaries_placed = sum(len(l) for l in index_lists)
  possible_boundaries = m - len(items)
  return boundaries_placed / float(possible_boundaries)

def random_segments(m, p_boundary):
  """
  Given a total mass and a probability of placing a boundary, return a
  randomly-generated list of segment masses.
  """
  indexes = list(ifilterfalse(lambda x: x is None, (
        (i if random() < p_boundary else None) for i in range(1, m) )))
  [masses] = indexes_to_masses([indexes], m)
  return masses

def total_mass(segmentations):
  total_masses = list(set([ sum(m) for m in segmentations.values() ]))
  assert len(total_masses) == 1
  return total_masses[0]

def main():
  "Produce a random segmentation for comparison purposes."
  args = parse_args()
  o = load_segmentation_data(args.filename)
  p_boundary = proportion_of_boundaries(o['items'])
  items = { d:{ 'random':random_segments(total_mass(s), p_boundary) }
            for d,s in o['items'].items() }
  rand = {
    'segmentation_type': 'linear',
    'id': 'random',
    'items': items }
  print json.dumps(rand, sort_keys=True)
  
if __name__ == "__main__":
  main()
