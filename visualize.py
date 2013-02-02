#! /usr/bin/env python

import os
import svg
from argparse import ArgumentParser
from functools import partial
from utils import *

STRIP_WIDTH = 150

def comparison_lines(compare, length, right_m):
  segmentations, color = compare
  assert len(segmentations) == 1
  [key] = segmentations.keys()
  masses = segmentations[key]
  [indexes], m = masses_to_indexes([masses])
  assert m == right_m
  return [ 
    svg.line(0, key, index, length=length, color=color, opacity='0.75')
    for index in indexes ]

def visualize(doc_id, segmentations, compare=[]):
  "Given segmentations, return an SVG visualization"
  [coders, mass_lists] = zip(*sorted(segmentations.items()))
  index_lists, m = masses_to_indexes(mass_lists)
  [lines,labels] = zip(*[ 
      (svg.line(coder_index, coder, index, dashed=True),
       svg.label(coder_index, index, index))
      for coder_index, coder in enumerate(coders)
      for index in index_lists[coder_index] ])
  comparisons = list(chain(*[ 
        comparison_lines(c, len(segmentations), m) for c in compare ]))
  return (svg.header(len(segmentations), m+1) +
          ''.join(lines) + ''.join(comparisons) + ''.join(labels) + svg.foot)

def write(filename, content):
  with open(filename, 'w') as out:
    out.write(content)

def main():
  "Produce SVG visualizations of segmentations."
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    '-c', '--compare', metavar='filename:color', action='append',
    help='name of a file with a segmentation to overlay for comparison, and a color to use')
  p.add_argument(
    '-o', '--output', help='directory to write SVG files to', 
    dest='dir', default='svg')
  args = p.parse_args()
  o = load_segmentation_data(args.filename)
  if args.compare:
    compare = [ (load_segmentation_data(f)['items'], color) 
                for f,color in 
                [ c.split(':') for c in args.compare if ':' in c ]]
  else:
    compare = []
  if not os.path.exists(args.dir):
    os.makedirs(args.dir)
  [ write('{}/{}.svg'.format(args.dir, doc_id.split(':')[1]),
          visualize(doc_id, segmentations, 
                    [ (d[doc_id], color) for d,color in compare ]))
    for doc_id, segmentations in o['items'].items() ]

if __name__ == "__main__":
  main()
