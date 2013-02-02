#! /usr/bin/env python
# -*- coding: utf-8 -*-

import operator
from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from functools import partial
from termcolor import colored
from utils import *

def count_judgments(index_lists):
  """
  Given a list of boundary index lists (one per coder), return a dict
  with the boundary indexes as keys and the number of times each index
  appeared in a list as the vals.
  """
  return reduce(lambda x,y: x+y, [ Counter(l) for l in index_lists ])

def pairwise_agreement(c, n):
  """
  Given a count `c` of coders and a count `n` of positive boundary
  judgments for an index, calculate the pairwise agreement on that
  index: the proportion of agreeing judgment pairs out of the total
  number of judgment pairs for that index.

  This is based on the formula given in Artstein & Poesio 2008. 
  """
  return (n*(n-1) + (c-n)*(c-n-1)) / float(c*(c-1))

def observed_agreement(c, m, judgments):
  """
  Given a count `c` of coders, a total mass `m`, and counts of
  positive boundary judgments for a list of indexes, calculate the
  observed agreement.

  This is based on the formula given in Artstein & Poesio 2008. 
  """
  boundary_agreements = [ pairwise_agreement(c, judgments[i]) 
                          for i in range(1, m) ]
  return sum(boundary_agreements) / len(boundary_agreements)

def expected_agreement(c, i, n, power=2):
  """
  Given a count `c` of coders, a count `i` of indexes (i.e. potential
  boundaries), and a count `n` of total positive boundary judgments,
  calculate the expected (due to chance) agreement using Fleiss’
  multi-π.

  This is based on the formula given in Artstein & Poesio 2008.  
  Note that the count of negative boundary judgments is c*i - n.
  """
  return (n**power + (c*i - n)**power) / float(i*c)**power

def variance_pi(c, i):
  """
  Calculate the variance for multi-π according to the formula in
  Fleiss, Joseph L., John C. Nee, and J. Richard Landis. Large Sample
  Variance of Kappa in the Case of Different Sets of Raters.
  Psychological Bulletin 86, no. 5 (1979): 974–977. 
  http://dx.doi.org/10.1037/0033-2909.86.5.974

  (Kappa is what Fleiss et al. call multi-π.)

  Note that because we only have two categories here, variance of
  multi-π is the same as variance in agreement on a category (equation
  13 in Fleiss et al).
  """
  return 2 / float(i*c*(c-1))

def multi_pi(segmentations):
  """
  Given coders' segmentations (represented as segment masses),
  calculate strict agreement on boundaries using Fleiss’s multi-π, and
  return the coefficient and its variance.
  """
  index_lists, m = masses_to_indexes(segmentations)
  judgments = count_judgments(index_lists)
  c = len(segmentations)
  o = observed_agreement(c, m, judgments)
  n = sum(judgments.values())
  e = expected_agreement(c, m-1, n)
  agreement = (o-e) / (1-e)
  var = variance_pi(c, m-1)
  return (agreement, var)

def show_results(title, per_document, overall):
  print '\n{}:\n'.format(title)
  print_coefficients(per_document)
  print
  print_coefficient('Overall', *overall)
  print

def merge(docs1, docs2):
  [doc_ids1, segmentations1] = zip(*sorted(docs1.items()))
  [doc_ids2, segmentations2] = zip(*sorted(docs2.items()))
  assert doc_ids1 == doc_ids2
  merged = map(lambda d1,d2: dict(d1.items() + d2.items()), 
               segmentations1, segmentations2)
  return dict(zip(doc_ids1, merged))

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    '-c', '--coder', help='only include specified coders', 
    action='append', dest='coders')
  p.add_argument(
    '-e', '--evaluate', help='name of a segmentation file to evaluate',
    metavar='filename')
  return p.parse_args()

def compare(values1, values2):
  """
  Given two coefficients and their variances, return the difference of
  the coefficients and the critical ratio (z-test).
  """
  c1, v1 = values1
  c2, v2 = values2
  return (c1-c2), ((c1-c2)/((v1+v2))**.5)

def format_comparison(d, val, comp):
  c,v = val
  drop,z = comp
  formatted = '{}: {} ({:.2f}, z: {:.2f})'.format(
    d.split(':')[-1], format_coefficient(c,v), drop, z)
  if z > 1.96 or z < -1.96:
    return colored(formatted, 'red')
  else:
    return formatted

def do(title, items, func, ref=None):
  per_document, overall = get_results(items, func)
  if ref:
    ref_per_document, ref_overall = ref
    values = sorted([ (doc_id, v, compare(v,ref_per_document[doc_id])) 
                       for doc_id,v in per_document.items() ],
                    key=lambda x: x[2][0], reverse=True)
    print '\n{}:\n'.format(title)
    print '\n'.join(
      [ format_comparison(d, val, comp) for d,val,comp in values ])
    print format_comparison('\nOverall', overall, compare(overall, ref_overall))
    print
  else:
    show_results(title, per_document, overall)
  return per_document, overall
  
def main():
  "Calculates strict segmentation agreement."
  args = parse_args()
  o = load_segmentation_data(args.filename)
  items = filter_coders(o['items'], args.coders) if args.coders else o['items']
  print '''
Strict segmentation agreement, where agreement is modeled as two
annotators making the same judgment on a potential boundary.'''
  ref = do('Fleiss’s multi-π, human coders', items, multi_pi) 
  if args.evaluate:
    e = load_segmentation_data(args.evaluate)
    do('With {}'.format(e['id']), merge(items, e['items']), multi_pi, ref)
    
if __name__ == "__main__":
  main()


