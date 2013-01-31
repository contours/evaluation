import json
import operator
from itertools import chain, groupby

def accumulate(iterable, func=operator.add):
  "accumulate([1,2,3,4,5]) --> 1 3 6 10 15"
  it = iter(iterable)
  total = next(it)
  yield total
  for element in it:
    total = func(total, element)
    yield total

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
  # make sure the segmentations are always in the same order by annotator
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

def load_segmentation_data(filename):
  with open(filename) as data:
    return json.load(data)  

def print_coefficients(d):
  for doc, c in sorted(d.items(), key=lambda x: x[1], reverse=True):
    print '{}: {:.2f}'.format(doc.split(':')[1], c) 

