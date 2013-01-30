#! /usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from itertools import permutations
from utils import *
from windowdiff import *

def pairwise_distance(judgments):
  """
  Given counts of label (number of boundaries) judgments, calculate
  the pairwise distance: sum over ordered pairs of labels of (label
  distance * product of label counts).
  """
  return sum([ judgments[a] * judgments[b] * ((a-b)**2)
        for a,b in permutations(judgments.keys(), 2) ])

def observed_disagreement(c, judgments):
  """
  Given a count `c` of coders, and counts of labels (number of
  boundaries judgments) for a list of windows, calculate the observed
  disagreement according to Krippendorf's α.
  """
  return (sum([ pairwise_distance(j) for j in judgments ]) 
          / float(len(judgments)*c*(c-1)))

def expected_disagreement(c, judgments):
  """
  Given a count `c` of coders, and counts of labels (number of
  boundaries judgments) for a list of windows, calculate the expected
  disagreement according to Krippendorf's α.
  """
  label_totals = reduce(lambda x,y: x+y, judgments)
  total_judgments = len(judgments)*c 
  return (pairwise_distance(label_totals)
          / float(total_judgments*(total_judgments-1)))

def near_agreement(segmentations, k=None):
  """
  Given coders' segmentations (represented as segment masses),
  calculate agreement on boundary counts within windows.
  """
  index_lists, m = masses_to_indexes(segmentations)
  if k is None: k = window_size(segmentations)
  judgments = count_window_judgments(index_lists, m, k)
  c = len(segmentations)
  o = observed_disagreement(c, judgments)
  e = expected_disagreement(c, judgments)
  return 1 - (o/e)

def main():
  "Calculates near segmentation agreement using Krippendorf's α."
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    '--reference', help='name of the reference annotator used to calculate k')
  args = p.parse_args()
  o = load_segmentation_data(args.filename)
  if args.reference is None:
    # Calculate window size per document
    agreement = near_agreement
  else:
    # Use one window size across all documents
    ra = 'annotators:{}'.format(args.reference)
    reference_segmentations = [ s[ra] for s in o['items'].values() ]
    k = int(round(mean_segment_mass(reference_segmentations) / 2))
    agreement = partial(near_agreement, k=k)
  print '''
Near segmentation agreement (Krippendorf's α), where agreement is
modeled as two annotators counting the same number of boundaries
within a window (i.e. WindowDiff):
'''
  print_coefficients(per_document_coefficients(o['items'], agreement))
  print '\nOverall agreement: {:.2f}\n'.format(
    overall_coefficient(o['items'], agreement))

if __name__ == "__main__":
  main()
