#! /usr/bin/env python

import redis
import json
from argparse import ArgumentParser
from utils import *

def speaker_masses(r, interview):
  speakers = [ r.hget(s, 'speaker') for s in r.lrange(
      'interviews:{}:sentences'.format(interview), 0, -1) ]
  interviewee = sorted((speakers.count(s),s) for s in set(speakers))[-1][1]
  def compare(pair):
    if interviewee in pair[1] and not pair[1][0] == pair[1][1]:
      # interviewee starting or finishing
      return pair[0]
    return None
  indexes = [ i for i in 
              map(compare, enumerate(pairwise(speakers), start=1)) 
              if i is not None ]
  [masses] = indexes_to_masses([indexes], len(speakers))
  return masses

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'interviews', nargs='+', help='interviews to get speaker masses of')
  return p.parse_args()

def main():
  args = parse_args()
  r = redis.StrictRedis()
  o = { 'id':'speakers', 
        'segmentation_type':'linear',
        'items':
          { 'interviews:{}'.format(interview): 
            { 'speakers':speaker_masses(r, interview) }
            for interview in args.interviews }}
  print json.dumps(o, sort_keys=True)

if __name__ == "__main__":
  main()
