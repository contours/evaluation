#! /usr/bin/env python

import redis
import json
from argparse import ArgumentParser
from utils import *

def speaker_masses(r, interview):
  speakers = [ r.hget(s, 'speaker') for s in r.lrange(
      'interviews:{}:sentences'.format(interview), 0, -1) ]
  indexes = [ i for i in 
              map(lambda pair: None if pair[1][0] == pair[1][1] else pair[0],
                  enumerate(pairwise(speakers), start=1)) if i is not None ]
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
