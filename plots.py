#! /usr/bin/env python

from argparse import ArgumentParser
from matplotlib import pyplot as plt
from numpy import median, arange
from strict_agreement import multi_pi
from utils import *

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument('filename', help='name of the JSON segmentation file')
  p.add_argument('svg', help='file to save the SVG figure as')
  return p.parse_args()

def items(per_document, overall):
  return sorted(per_document.items() + [('overall',overall)])

def same(sequences):
  return all(len(set(z)) == 1 for z in zip(*sequences))

def merge_results(*results):
  keys, values = zip(*[ zip(*items(*r)) for r in results ])
  assert same(keys)
  # sort by median value
  return zip(*sorted(zip(keys[0], *values), 
                     key=lambda x: median(zip(*x[1:])[0])))

def main():
  args = parse_args()
  o = load_segmentation_data(args.filename)
  keys, values = merge_results(get_results(o['items'], multi_pi))
  [coefficients, variances] = zip(*values)
  labels = [ k.split(':')[-1] for k in keys ]
  pos = arange(len(labels)) + .5
  plt.yticks(pos, labels)
  plt.xlim(0, 1)
  plt.ylim(0, len(labels))
  plt.grid(axis='y')
  errors = [ error(v) for v in variances ]
  guides = [ error(v, 0.5) for v in variances ]
  plt.errorbar(coefficients, pos, xerr=errors,
               fmt='o', color='black', capsize=0, 
               label=r'multi-$\pi$ on boundaries')
  plt.errorbar(coefficients, pos, xerr=guides, 
               fmt=None, ecolor='black', label=r'_nolegend_')
  plt.legend(loc='lower right', numpoints=1)
  plt.savefig(args.svg, format='svg', transparent=True)

if __name__ == "__main__":
  main()
