# -*- coding: utf-8 -*-

import json
import operator
from itertools import chain, groupby, tee, izip

def pairwise(iterable):
  "s -> (s0,s1), (s1,s2), (s2, s3), ..."
  a, b = tee(iterable)
  next(b, None)
  return izip(a, b)

def accumulate(iterable, func=operator.add):
  "accumulate([1,2,3,4,5]) --> 1 3 6 10 15"
  it = iter(iterable)
  total = next(it)
  yield total
  for element in it:
    total = func(total, element)
    yield total

def masslist_to_indexlist(masslist):
  [indexlist], m = masses_to_indexes([masslist])
  return indexlist, m

def masses_to_indexes(mass_lists):
  """
  Convert segmentations represented as mass sequences to segmentations
  represented as boundary index sequences, plus total mass.
  """
  sums = [ list(accumulate(m)) for m in mass_lists ]
  [index_lists, total_masses] = zip(*[ (l[:-1],l[-1]) for l in sums ])
  assert 1 == len(set(total_masses)) # make sure they all add up the same
  return index_lists, total_masses[0]

def zip_differences(l):
  return [ operator.sub(*pair) for pair in zip(l[1:], l[0:]) ]

def indexlist_to_masslist(indexlist, m):
  [masslist] = indexes_to_masses([indexlist], m)
  return masslist

def indexes_to_masses(index_lists, m):
  """
  Given a total mass `m`, convert segmentations represented as
  boundary index sequences to segmentations represented as mass
  sequences.
  """
  return [ zip_differences([0] + l + [m]) for l in index_lists ]

def assert_same_coders(documents):
  coders = [ set(segmentations.keys()) for segmentations in documents.values() ]
  assert set.intersection(*coders) == set.union(*coders)

def per_document_coefficients(documents, f):
  """
  Expects a dict with document IDs as keys and ``{coder:segmentation}`` 
  dicts as values. Note that each document must have the same set of 
  coders, or an exception will be thrown.
  """
  assert_same_coders(documents)
  # make sure the segmentations are always in the same order
  return { doc_id: f([ segs[a] for a in sorted(segs) ] )
           for doc_id, segs in documents.items() }

def flattened(dicts):
  "Flatten a sequence of dictionaries into a single sequence of tuples."
  return list(chain(*[d.items() for d in dicts]))

def overall_segmentations(documents):
  """
  Expects a dict with document IDs as keys and ``{coder:segmentation}`` 
  dicts as values. Note that each document must have the same set of 
  coders, or an exception will be thrown.
  """
  assert_same_coders(documents)
  # make sure segmentations are in document order
  [doc_ids, segmentations] = zip(*sorted(documents.items())) 
  key = lambda x: x[0]
  return [ list(chain(*[ x[1] for x in g ])) 
           for c,g in groupby(sorted(flattened(segmentations), key=key), key) ]

def overall_coefficient(documents, f):
  return f(overall_segmentations(documents))

def get_results(documents, f):
  return (per_document_coefficients(documents, f), 
          overall_coefficient(documents, f))

def load_segmentation_data(filename):
  with open(filename) as data:
    return json.load(data)  

def error(variance, interval=0.95):
  if interval == 0.95:
    return 1.96*(variance**.5)
  if interval == 0.5:
    return 0.67*(variance**.5)
  raise Exception('interval must be .95 or .5')

def format_coefficient(c, v):
  return '{:.2f}±{:.2f}'.format(c, error(v)) 

def print_coefficient(label, c, v):
  print '{}: {:.2f}±{:.2f}'.format(label, c, error(v)) 

def print_coefficients(d):
  for doc, (c,v) in sorted(d.items(), key=lambda x: x[1], reverse=True):
    print_coefficient(doc.split(':')[1], c, v)

def filter_coders(documents, keep):
  [doc_ids, segmentations] = zip(*sorted(documents.items()))
  filtered = [ { k:v for k,v in s.items() if k in keep } 
               for s in segmentations ]
  return dict(zip(doc_ids, filtered))

