#! /usr/bin/env python
# -*- coding: utf-8 -*-

import operator
from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from functools import partial
from termcolor import colored
from utils import *

# Notes on terminology: 
#
# "Mass" is simply a count of units (e.g. sentences) in a segment or
# document.

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
  """
  return (n*(n-1) + (c-n)*(c-n-1)) / float(c*(c-1))

def proportion_positive(c, i, n):
  return n / float(i*c)

def observed_agreement(c, m, judgments):
  """
  Given a count `c` of coders, a total mass `m`, and counts of
  positive boundary judgments for a list of indexes, calculate the
  observed agreement.
  """
  boundary_agreements = [ pairwise_agreement(c, judgments[i]) 
                          for i in range(1, m) ]
  return sum(boundary_agreements) / len(boundary_agreements)

def observed_agreement_on_positive(c, m, judgments):
  i = m-1
  p = proportion_positive(c, i, sum(judgments.values()))
  num = sum([ n**2 for n in judgments.values() ]) - (i*c*p)
  den = i*c*(c-1)*p
  return num / den

def estimate_pos(c, index_lists, m):
  "The proportion of positive judgments made by the specified coder"
  return len(index_lists[c]) / float(m-1)

def estimate_neg(c, index_lists, m):
  "The proportion of negative judgments made by the specified coder"
  return (m-1-len(index_lists[c])) / float(m-1)

def joint(pairs, estimate, index_lists, m):
  "Joint probability for an arbitrary pair of coders"
  return sum([ estimate(a, index_lists, m) * estimate(b, index_lists, m)
               for a,b in pairs ]) / len(pairs)

def expected_agreement_kappa(index_lists, m):
  """
  Given a list of boundary index lists (one per coder) and a total mass `m`,
  calculate the expected (due to chance) agreement using Fleiss' multi-κ.
  """
  coders = range(len(index_lists))
  pairs = list(combinations(coders, 2))
  return (joint(pairs, estimate_pos, index_lists, m) +
          joint(pairs, estimate_neg, index_lists, m))

def expected_agreement_pi(c, i, n, power=2):
  """
  Given a count `c` of coders, a count `i` of indexes (i.e. potential
  boundaries), and a count `n` of total positive boundary judgments,
  calculate the expected (due to chance) agreement using Fleiss’
  multi-π.
  
  Note that the count of negative boundary judgments is c*i - n.
  """
  return (n**power + (c*i - n)**power) / float(i*c)**power

# def variance_pi(e, c, i, n):
#   """
#   Given an expected agreement `e`, a count `c` of coders, a count `i`
#   of indexes (i.e. potential boundaries), and a count `n` of total
#   positive boundary judgments, calculate the variance of Fleiss’
#   multi-π.
#   """
#   w = 2 / float(i*c*(c-1))
#   x = ((2*c)-3)*(e**2)
#   y = (2*(c-2)*expected_agreement_pi(c,i,n,power=3)) / ((i*c)**3)
#   z = (1-e)**2
#   return w * ((e-x+y) / z)

# def variance_pi(c, i, n):
#   return (n - n**2) / float(i*c*(i*c - 1))

def variance_pi(c, i):
  """
  Calculate the variance for multi-π according to the formula in
  Fleiss, Joseph L., John C. Nee, and J. Richard Landis. Large Sample
  Variance of Kappa in the Case of Different Sets of Raters.
  Psychological Bulletin 86, no. 5 (1979): 974–977. 
  http://dx.doi.org/10.1037/0033-2909.86.5.974

  Note that because we only have two categories here, variance of
  multi-π is the same as variance in agreement on a category (equation
  13 in Fleiss, Nee, and Landis).
  """
  return 2 / float(i*c*(c-1))

def strict_agreement(segmentations, expected_agreement='pi'):
  """
  Given coders' segmentations (represented as segment masses),
  calculate strict agreement on boundaries.
  """
  index_lists, m = masses_to_indexes(segmentations)
  judgments = count_judgments(index_lists)
  c = len(segmentations)
  o = observed_agreement(c, m, judgments)
  n = sum(judgments.values())
  if expected_agreement == 'pi':
    e = expected_agreement_pi(c, m-1, n)
  elif expected_agreement == 'kappa':
    e = expected_agreement_kappa(index_lists, m)
  agreement = (o-e) / (1-e)
  var = variance_pi(c, m-1)
  print var
  return (agreement, var)

def variance_pi_on_positive(e, c, i, n):
  x = (1+(2*(c-1)*e))**2
  y = 2*(c-1)*e*(1-e)
  z = i*c*((c-1)**2)*e*(1-e)
  return (x+y)/z

def strict_agreement_on_positive(segmentations):
  index_lists, m = masses_to_indexes(segmentations)
  judgments = count_judgments(index_lists)
  c = len(segmentations)
  o = observed_agreement_on_positive(c, m, judgments)
  n = sum(judgments.values())
  e = proportion_positive(c, m-1, n)
  agreement = (o-e) / (1-e)
  var = variance_pi_on_positive(e, c, m-1, n)
  return (agreement, var)

def annotator_bias(segmentations):
  index_lists, m = masses_to_indexes(segmentations)
  judgments = count_judgments(index_lists)
  c = len(segmentations)
  return (expected_agreement_pi(c, m-1, sum(judgments.values())) -
          expected_agreement_kappa(index_lists, m))

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
  p.add_argument(
    '-k', '--kappa', help='also calculate multi-κ agreement and bias', 
    action='store_true')
  return p.parse_args()

def compare(values1, values2):
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
  #pi = partial(strict_agreement, expected_agreement='pi')
  pi = strict_agreement_on_positive
  ref = do('Fleiss’s multi-π, human coders', items, pi) 
  if args.evaluate:
    e = load_segmentation_data(args.evaluate)
    do('With {}'.format(e['id']), merge(items, e['items']), pi, ref)
  if args.kappa:
    kappa = partial(strict_agreement, expected_agreement='kappa')
    do('Fleiss’s multi-κ', items, kappa)
    do('Annotator bias', items, annotator_bias)
    
if __name__ == "__main__":
  main()


