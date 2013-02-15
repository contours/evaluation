#! /usr/bin/env python

import os
import svg
from argparse import ArgumentParser
from functools import partial
from utils import *

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

def visualize(doc_id, segmentations, 
              compare=[], tick_masses=None, highlight_masses=None):
  "Given segmentations, return an SVG visualization"
  [coders, mass_lists] = zip(*sorted(segmentations.items()))
  index_lists, m = masses_to_indexes(mass_lists)
  if tick_masses:
    tick_indexes, tick_m = masses_to_indexes(tick_masses)
    assert tick_m == m
    ticks = [ svg.tick(i) for i in tick_indexes[0] ]
  else:
    ticks = []
  if highlight_masses:
    highlight_indexes, highlight_m = masses_to_indexes(highlight_masses)
    assert highlight_m == m
    highlights = [ svg.highlight(y,l) 
                   for y,l in zip([0] + highlight_indexes[0], 
                                  highlight_masses[0])[1::2] ]
  else:
    highlights = []
  [lines,labels] = zip(*[ 
      (svg.line(coder_index, coder, index, dashed=True),
       svg.label(coder_index, index, index))
      for coder_index, coder in enumerate(coders)
      for index in index_lists[coder_index] ])
  comparisons = list(chain(*[ 
        comparison_lines(c, len(segmentations), m) for c in compare ]))
  return (svg.header(len(segmentations), m+1)
          + ''.join(highlights) + ''.join(ticks) + ''.join(lines) 
          + ''.join(comparisons) + ''.join(labels) + svg.foot)

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
    help='name segmentation file to overlay for comparison, and a color to use')
  p.add_argument(
    '-t', '--ticks', metavar='filename',
    help='name of segmentation file to use for adding ticks')
  p.add_argument(
    '-l', '--highlight', metavar='filename',
    help='name of segmentation file to use for adding highlights')
  p.add_argument(
    '-o', '--output', help='directory to write SVG files to', 
    dest='dir', default='svg')
  args = p.parse_args()
  o = load_segmentation_data(args.filename)
  if args.ticks:
    ticks = load_segmentation_data(args.ticks)['items']
  else:
    ticks = {}
  if args.highlight:
    highlight = load_segmentation_data(args.highlight)['items']
  else:
    highlight = {}
  if args.compare:
    compare = [ (load_segmentation_data(f)['items'], color) 
                for f,color in 
                [ c.split(':') for c in args.compare if ':' in c ]]
  else:
    compare = []
  if not os.path.exists(args.dir):
    os.makedirs(args.dir)
  [ write('{}/{}.svg'.format(args.dir, doc_id.split(':')[1]),
          visualize(doc_id, 
                    segmentations, 
                    [ (d[doc_id], color) for d,color in compare ],
                    ticks[doc_id].values() if doc_id in ticks else None,
                    highlight[doc_id].values() if doc_id in highlight else None))
    for doc_id, segmentations in o['items'].items() ]

if __name__ == "__main__":
  main()
