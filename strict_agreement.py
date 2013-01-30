#! /usr/bin/env python
# -*- coding: utf-8 -*-

import operator
from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from functools import partial
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

def observed_agreement(c, m, judgments):
  """
  Given a count `c` of coders, a total mass `m`, and counts of
  positive boundary judgments for a list of indexes, calculate the
  observed agreement.
  """
  boundary_agreements = [ pairwise_agreement(c, judgments[i]) 
                          for i in range(1, m) ]
  return sum(boundary_agreements) / len(boundary_agreements)

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

def expected_agreement_pi(c, i, n):
  """
  Given a count `c` of coders, a count `i` of indexes (i.e. potential
  boundaries), and a count `n` of total positive boundary judgments,
  calculate the expected (due to chance) agreement using Fleiss’
  multi-π.
  
  Note that the count of negative boundary judgments is c*i - n.
  """
  return (n**2 + (c*i - n)**2) / float(i*c)**2

def strict_agreement(segmentations, expected_agreement='pi'):
  """
  Given coders' segmentations (represented as segment masses),
  calculate strict agreement on boundaries.
  """
  index_lists, m = masses_to_indexes(segmentations)
  judgments = count_judgments(index_lists)
  c = len(segmentations)
  o = observed_agreement(c, m, judgments)
  if expected_agreement == 'pi':
    e = expected_agreement_pi(c, m-1, sum(judgments.values()))
  elif expected_agreement == 'kappa':
    e = expected_agreement_kappa(index_lists, m)
  return (o-e) / (1-e)

def annotator_bias(segmentations):
  index_lists, m = masses_to_indexes(segmentations)
  judgments = count_judgments(index_lists)
  c = len(segmentations)
  return (expected_agreement_pi(c, m-1, sum(judgments.values())) -
          expected_agreement_kappa(index_lists, m))

def get_results(documents, f):
  return (per_document_coefficients(documents, f), 
          overall_coefficient(documents, f))

def show_results(title, documents, f):
  per_document, overall = get_results(documents, f)
  print '\n{}:\n'.format(title)
  print_coefficients(per_document)
  print '\nOverall: {:.2f}\n'.format(overall)

def main():
  "Calculates strict segmentation agreement."
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    '-k', '--kappa', help='also calculate multi-κ agreement and bias', 
    action='store_true')
  args = p.parse_args()
  o = load_segmentation_data(args.filename)
  print '''
Strict segmentation agreement, where agreement is modeled as two
annotators making the same judgment on a potential boundary.
'''
  show_results(
    'Fleiss’s multi-π', o['items'],
    partial(strict_agreement, expected_agreement='pi'))
  if args.kappa:
    show_results(
      'Fleiss’s multi-κ', o['items'],
      partial(strict_agreement, expected_agreement='kappa'))
    show_results(
      'Annotator bias', o['items'], annotator_bias)
    
if __name__ == "__main__":
  main()


