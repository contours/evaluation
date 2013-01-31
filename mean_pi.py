#! /usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from utils import *

def observed_agreement(i, c, g):
  """
  Given a number of boundaries `i`, a coder's indexes `c`, and gold
  indexes `g`, calculate the observed agreement according to π.
  """
  agreed_pos = len(set.intersection(set(c), set(g)))
  agreed_neg = i - len(set.union(set(c), set(g)))
  return (agreed_pos + agreed_neg) / float(i)

def expected_agreement(i, n):
  """
  Given a number of boundaries `i` and a number of positive judgments
  `n` calculate the expected agreement according to π.
  """
  return (n**2 + (2*i-n)**2) / float(4*(i**2))

def pi(c, g, m):
  """
  Given a coder's indexes `c`, gold indexes `g`, and total mass `m`,
  calculate agreement according to π.
  """
  o = observed_agreement(m-1, c, g)
  e = expected_agreement(m-1, len(c)+len(g))
  return (o-e) / (1-e)

def pis(segmentations, gold_masses):
  """
  Given coders' segmentations and a gold segmentation (represented as
  segment masses), calculate mean agreement with gold.
  """
  index_lists, m = masses_to_indexes(segmentations)
  [gold_indexes], gold_m = masses_to_indexes([gold_masses])
  assert gold_m == m
  return [ pi(c, gold_indexes, m) for c in index_lists ]

def mean(s):
  return sum(s) / float(len(s))

def main():
  "Calculate mean π against a gold segmentation."
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    'gold', help='name of the gold segmentation file')
  args = p.parse_args()
  o = load_segmentation_data(args.filename)
  g = load_segmentation_data(args.gold)['items']
  all_pis = { i: pis(segmentations.values(), g[i]['gold'])
              for i, segmentations in sorted(o['items'].items()) }
  means = { i: mean(pis) for i,pis in all_pis.items() }
  print '''
Mean strict agreement with a "gold" segmentation, where agreement is
modeled as a coder making the same judgment as the majority.
'''
  print 'Mean π:\n'
  print_coefficients(means)
  print '\nOverall: {:.2f}'.format(mean(list(chain(*all_pis.values()))))
  
if __name__ == "__main__":
  main()
