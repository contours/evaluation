#! /usr/bin/env python

from argparse import ArgumentParser
from functools import partial
from itertools import *
from operator import sub
from utils import *
from windowdiff import window_size

def length(interview):
  interview_id = interview.split(':')[1]
  with open('{}.txt'.format(interview_id)) as t:
    return len(t.readlines())

def every_nth(n, *iterables):
  "Given a sequence of iterables, return every nth item"
  return islice(chain(*iterables), n-1, None, n)

def unique_everseen(iterable, key=None):
  "List unique elements, preserving order. Remember all elements ever seen."
  seen = set()
  seen_add = seen.add
  if key is None:
    for element in ifilterfalse(seen.__contains__, iterable):
      seen_add(element)
      yield element
  else:
    for element in iterable:
      k = key(element)
      if k not in seen:
        seen_add(k)
        yield element

def near_intersection(window, s1, s2):
  # take distances of pairs of values from the two sets
  pairs = ((abs(x-y),x,y) for x,y in product(s1,s2))
  # filter out ones with distance >= window
  filtered = ifilter(lambda x: x[0] < window, pairs)
  # order by distance and first value
  key = lambda x:x[:2]
  ordered = sorted(filtered, key=key)
  # filter out repeated second values
  unique = unique_everseen(ordered, key=lambda x:x[2])
  # group by distance and first value
  grouped = groupby(unique, key=key)
  # merge equidistant indexes
  merged = [ k + tuple(every_nth(3,*g)) for k,g in grouped ]
  # take means to get consensus indexes
  return set((sum(s[1:])/len(s[1:])) for s in merged)

def merge_small_segments(masses, window):
  to_merge = 0
  merged = []
  for m in masses:
    if m < window:
      to_merge += m
    else:
      if to_merge > 0:
        if len(merged) > 0:
          to_merge,r = divmod(to_merge,2)
          merged[-1] += (to_merge+r)
      merged.append(m+to_merge)
      to_merge = 0
  merged[-1] += to_merge
  return merged

def derive_gold(segmentations, near=False):
  if near:
    window = window_size(segmentations)
    intersect = partial(near_intersection, window)
  else:
    intersect = set.intersection
  index_lists, m = masses_to_indexes(segmentations)
  index_sets = [ set(l) for l in index_lists ]
  intersections = [ intersect(*pair) for pair in combinations(index_sets, 2) ]
  gold_indexes = sorted(set.union(*intersections))
  [gold_masses] = indexes_to_masses([gold_indexes], m)
  if near:
    return { 'gold': merge_small_segments(gold_masses, window) }
  else:
    return { 'gold': gold_masses }

def main():
  "Generates a 'gold' segmentation by majority vote."
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'filename', help='name of the JSON segmentation file')
  p.add_argument(
    '-n', '--near', action='store_true',
    help='count near agreement when majority voting')
  args = p.parse_args()
  o = load_segmentation_data(args.filename)
  gold = { 'id':o['id'], 'segmentation_type':'linear' }
  gold['items'] = { 
    interview: derive_gold(segmentations.values(), args.near) 
    for interview, segmentations in o['items'].items() }
  print json.dumps(gold, sort_keys=True)
      
if __name__ == "__main__":
  main()
