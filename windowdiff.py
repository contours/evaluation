from collections import Counter
from itertools import islice, tee, izip, chain

def consume(iterator, n):
  "Advance the iterator `n` steps ahead."
  next(islice(iterator, n, n), None)

def windowed(iterator, size):
  "Slide a window of the specified `size` through an iterator."
  iterators = tee(iterator, size)
  [ consume(iterators[i], i) for i in range(1,size) ]
  return izip(*iterators)

def mean_segment_mass(segmentations):
  all_segments = list(chain(*segmentations))
  return sum(all_segments) / float(len(all_segments))

def window_size(segmentations):
  "k is half the mean segment mass"
  return int(round(mean_segment_mass(segmentations) / 2))

def count_window_judgments(index_lists, m, k):
  """
  Given a list of boundary index lists (one per coder), a total mass
  `m`, and a window size `k`, return a list containing the label
  (number of boundaries) counts for each window of size `k`.
  """
  index_counts = [ Counter(l) for l in index_lists ]
  windows = list(windowed(range(1,m), k))
  labels_by_coder = [[ sum([ c[i] for i in w ]) for w in windows ]
                     for c in index_counts ]
  labels_by_window = zip(*labels_by_coder)
  return [ Counter(labels) for labels in labels_by_window ]


