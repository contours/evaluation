#! /usr/bin/env python

import redis
import json
from argparse import ArgumentParser

def speechblock_mass(r, speechblock):
  mass = r.llen('{}:sentences'.format(speechblock))
  assert mass > 0, 'speechblock {} has zero mass'.format(speechblock)
  return mass

def speechblock_masses(r, interview):
  speechblocks = 'interviews:{}:speechblocks'.format(interview)
  return [ speechblock_mass(r,k) for k in r.lrange(speechblocks, 0, -1) ]

def parse_args():
  p = ArgumentParser(description=main.__doc__)
  p.add_argument(
    'interviews', nargs='+', help='interviews to get speechblock masses of')
  return p.parse_args()

def main():
  args = parse_args()
  r = redis.StrictRedis()
  o = { 'id':'speechblocks', 
        'segmentation_type':'linear',
        'items':
          { 'interviews:{}'.format(interview): 
            { 'speechblocks':speechblock_masses(r, interview) }
            for interview in args.interviews }}
  print json.dumps(o, sort_keys=True)

if __name__ == "__main__":
  main()
