#! /usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from functools import partial
from utils import *
from windowdiff import *

def pairwise_agreement(c, k, judgments):
  """
  Given a count `c` of coders, a window size `k`, and counts of label
  (number of boundaries) judgments for a window, calculate the
  pairwise agreement on that window: the proportion of agreeing
  judgment pairs out of the total number of judgment pairs for that
  window.
  """
  return (sum([ judgments[label]*(judgments[label]-1) for label in range(k+1) ])
          / float(c*(c-1)))

def observed_agreement(c, k, judgments):
  """
  Given a count `c` of coders, a window size `k`, and counts of
  labels (number of boundaries judgments) for a list of windows,
  calculate the observed agreement.
  """
  window_agreements = [ pairwise_agreement(c, k, j) for j in judgments ]
  return sum(window_agreements) / len(window_agreements)

def expected_agreement_pi(judgments):
  """
  Given counts of labels (number of boundaries judgments) for a list
  of windows, calculate the expected (due to chance) agreement
  according to Fleiss’s multi-π.
  """
  label_totals = reduce(lambda x,y: x+y, judgments).values()
  return sum([ n**2 for n in label_totals ]) / float(sum(label_totals))**2

def near_agreement(segmentations, k=None, 
                   expected_agreement=expected_agreement_pi):
  """
  Given coders' segmentations (represented as segment masses),
  calculate agreement on boundary counts within windows.
  """
  index_lists, m = masses_to_indexes(segmentations)
  if k is None: k = window_size(segmentations)
  judgments = count_window_judgments(index_lists, m, k)
  c = len(segmentations)
  o = observed_agreement(c, k, judgments)
  e = expected_agreement_pi(judgments)
  return (o-e) / (1-e)

def main():
  "Calculates near segmentation agreement using Fleiss’s multi-π."
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
Near segmentation agreement (Fleiss’s multi-π), where agreement is
modeled as two annotators counting the same number of boundaries
within a window (i.e. WindowDiff):
'''
  print_coefficients(per_document_coefficients(o['items'], agreement))
  print '\nOverall agreement: {:.2f}\n'.format(
    overall_coefficient(o['items'], agreement))

if __name__ == "__main__":
  main()
