#! /usr/bin/env python

import os
import svg
from argparse import ArgumentParser
from functools import partial
from utils import *

STRIP_WIDTH = 150

def visualize(segmentations, gold_masses=None):
  "Given segmentations, return an SVG visualization"
  [coders, mass_lists] = zip(*sorted(segmentations.items()))
  index_lists, m = masses_to_indexes(mass_lists)
  [lines,labels] = zip(*[ 
      (svg.line(coder_index, coder, index, dashed=True),
       svg.label(coder_index, index, index))
      for coder_index, coder in enumerate(coders)
      for index in index_lists[coder_index] ])
  if gold_masses:
    [gold_indexes], gold_m = masses_to_indexes([gold_masses])
    assert gold_m == m
  else:
    gold_indexes = []
  gold_lines = [ svg.line(0, 'gold', index, length=len(segmentations), 
                          color='#ff0000', opacity='0.75')
                 for index in gold_indexes ]
  return (svg.header(len(segmentations), m+1) +
          ''.join(lines) + ''.join(gold_lines) + ''.join(labels) + svg.foot)

def write(filename, content):
  with open(filename, 'w') as out:
    out.write(content)

def main():
  "Produce SVG visualizations of segmentations."
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    '-o', '--output', help='directory to write SVG files to', 
    dest='dir', default='svg')
  p.add_argument(
    '-g', '--gold', help='name of a gold segmentation file')
  args = p.parse_args()
  o = load_segmentation_data(args.filename)
  g = load_segmentation_data(args.gold)['items'] if args.gold else None
  if not os.path.exists(args.dir):
    os.makedirs(args.dir)
  [ write('{}/{}.svg'.format(args.dir, i.split(':')[1]),
          visualize(segmentations, g[i]['gold'] if g else None))
    for i, segmentations in o['items'].items() ]

if __name__ == "__main__":
  main()
