#! /usr/bin/env python

import re
import sys
import json
import redis
from Queue import Queue, Empty
from functools import partial, wraps
from itertools import chain, ifilterfalse, groupby
from lxml import etree
from subprocess import Popen, PIPE
from threading import Thread
from types import UnicodeType

def enqueue_output(out, queue):
  [ queue.put(line) for line in iter(out.readline, b'') ]
  out.close()

def launch_splitta():
  ON_POSIX = 'posix' in sys.builtin_module_names
  p = Popen(['splitta'], stdin=PIPE, stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
  q = Queue()
  t = Thread(target=enqueue_output, args=(p.stdout, q))
  t.daemon = True # thread dies with the program
  t.start()
  return p,q

def memoize(f):
  @wraps(f)
  def wrapper(*args):
    assert len(args) == 1
    arg = args[0]
    if arg not in cache:
      cache[arg] = f(arg)
    return cache[arg]
  return wrapper

cache = {}

@memoize
def split(text):
  p,q = launch_splitta()
  p.stdin.write(text.encode('utf-8'))
  p.stdin.close()
  lines = []
  while True:
    try:  
      lines.append(q.get(timeout=.01).decode('utf-8')[:-1])
    except Empty:
      if len(lines) > 0:
        return lines

def clean(text):
  assert type(text) is UnicodeType, 'Bad text: {}'.format(text)
  return re.sub('\s+', ' ', text).strip()

def sentences(e):
  return [ split(clean(etree.tostring(p, method='text', encoding='unicode'))) 
           for p in e.xpath('p') ]

def get_speakers(interview):
  tree = etree.parse(
    '/Users/ryanshaw/Data/sohp/docsouth/{}.xml'.format(interview))
  return [ (e[0].text.strip(' :'), sentences(e)) for e in tree.xpath('//sp') ]

def read_cache():
  try:
    with open('cache.json') as f:
      cache = json.load(f) 
  except IOError:
    cache = {}
  return cache

def write_cache():
  with open('cache.json', 'w') as f:
    json.dump(cache, f) 

class PeekableIterator:
  def __init__(self, iterable):
    self.iter = iter(iterable)
    self.queue = []
  def __iter__(self):
    return self
  def next(self):
    if self.queue:
      return self.queue.pop()
    else:
      return self.iter.next()
  def push(self, x):
    self.queue.append(x)

def sametext(x_s, r_s):
  if type(x_s) is UnicodeType:
    x_text = x_s
  else:
    x_text = x_s[u'text']
  if type(r_s) is UnicodeType:
    r_text = r_s
  else:
    r_text = r_s[u'text']
  return x_text.replace(u' ',u'') == r_text.replace(u' ',u'')

def align(x_sentences, r_sentences):
  x_iter = PeekableIterator(x_sentences)
  r_iter = PeekableIterator(r_sentences)
  while True:
    x_s = x_iter.next()
    r_s = r_iter.next()
    if sametext(x_s,r_s):
      yield x_s,r_s
    else:
      x_next_s = x_iter.next()
      r_next_s = r_iter.next()
      if sametext(x_next_s,r_s):
        # 1 dropped sentence
        yield x_next_s,r_s
        r_iter.push(r_next_s)
      elif sametext(x_s[u'text']+x_next_s[u'text'], r_s):
        # combined sentence
        yield x_s,r_s
        r_iter.push(r_next_s)
      elif sametext(x_s, r_s[u'text']+r_next_s[u'text']):
        # split sentence
        yield x_s,r_s
        yield x_s,r_next_s
        x_iter.push(x_next_s)
      elif sametext(x_s[u'text']+x_next_s[u'text'],
                    r_s[u'text']+r_next_s[u'text']):
        # stray bracket
        yield x_s,r_s
        yield x_next_s,r_next_s
      else:
        x_next_next_s = x_iter.next()
        if sametext(x_next_next_s,r_s[u'text']):
          # 2 dropped sentences
          yield x_next_next_s,r_s
          r_iter.push(r_next_s)
        else:
          raise Exception('\n' + '\n\n'.join(
              [ dict2str(s) for s in (x_s, x_next_s, x_next_next_s,
                                      r_s, r_next_s) ]))

def flatten_speechblock(index, block):
  speechblock = u'speechblocks:{}/{}'.format(
    block['interview'].split(':')[1], index+1)
  return [ {
      u'text':s,
      u'index':unicode(i),
      u'speechblock':speechblock,
      u'speaker':block['speaker'],
      u'interview':block['interview']
      } for i,s in enumerate(block['sentences']) ] 

def flatten_speaker(interview, speaker, blocks):
  return [ {
      u'sentences':b,
      u'speaker':u'speakers:{}/{}'.format(interview, speaker),
      u'interview':u'interviews:{}'.format(interview),
      } for b in blocks ]

def get_sentences(interview):
  speechblocks = chain(
    *[ flatten_speaker(interview, speaker, blocks) 
       for speaker, blocks in get_speakers(interview) ])
  sentences = chain(
    *[ flatten_speechblock(i,b) for i,b in enumerate(speechblocks) ])
  return list(sentences)

def dict2str(d):
  return '\n'.join([ u'{}: {}'.format(k,v) for k,v, in sorted(d.items()) ])

def show(x_s, r_s):
  return u'\n{}\n{}'.format(dict2str(x_s), dict2str(r_s))

def aligns_with(x_s, r_s):
  x_text = x_s[u'text'].replace(u' ',u'')
  r_text = r_s[u'text'].replace(u' ',u'')
  return (x_text.startswith(r_text) or 
          x_text.endswith(r_text) or 
          r_text.startswith(x_text) or 
          r_text.endswith(x_text))

def fix_sentence(x_s, r_s):
  assert set(x_s.keys()) == set(r_s.keys()), show(x_s,r_s)
  assert x_s['interview'] == r_s['interview'], show(x_s,r_s)
  assert aligns_with(x_s,r_s), show(x_s,r_s)
  r_items = [ (k,r_s[k]) for k in (u'interview',u'text') ]
  x_items = [ (k,x_s[k]) for k in (u'index',u'speechblock',u'speaker') ]
  return dict(r_items + x_items)

def fix_interview(r, interview):
  x_sentences = get_sentences(interview)
  [r_keys,r_sentences] = zip(*[ (k, r.hgetall(k)) for k in r.lrange(
        'interviews:{}:sentences'.format(interview), 0, -1) ])
  aligned = list(align(x_sentences, r_sentences))
  assert len(aligned) == len(r_sentences)
  fixed = [ fix_sentence(x_s,r_s) for x_s,r_s in aligned ]
  return r_keys, r_sentences, fixed

def save(o, filename):
  with open(filename, 'w') as f:
    json.dump(o, f, sort_keys=True, indent=2, separators=(',', ': '))

def ifdigit(s):
  if s.isdigit():
    return int(s)
  return s

def sortkey(k):
  return [ (int(s) if s.isdigit() else s) for s in re.split(r':|/', k) ]

def set_list(r, key, values):
  r.delete(key)
  r.rpush(key, *sorted(set(values), key=sortkey))

def index_by(r, items, field, index, val=lambda x: x[0]):
  key = lambda x: x[1][field]
  [ set_list(r, '{}:{}'.format(k,index),  [ val(x) for x in g ])
    for k,g in groupby(sorted(items, key=key), key=key) ]

def update(r, items):
  [ r.hmset(k,v) for k,v in items ]
  index_by(r, items, 'speaker', 'sentences')
  index_by(r, items, 'speechblock', 'sentences')
  index_by(r, items, 'speaker', 'speechblocks', lambda x: x[1]['speechblock'])
  index_by(r, items, 'interview', 'speechblocks', lambda x: x[1]['speechblock'])
  index_by(r, items, 'interview', 'speakers', lambda x: x[1]['speaker'])

def main(interviews):
  r = redis.StrictRedis(decode_responses=True)
  [keys,original,fixed] = zip(*[ fix_interview(r,i) for i in interviews ])
  o = dict(zip(chain(*keys),chain(*original)))
  f = dict(zip(chain(*keys),chain(*fixed)))
  save(o, 'original.json')
  save(f, 'fixed.json')
  update(r, f.items())

if __name__ == "__main__":
  interviews = [
    'U-0005',
    'U-0007',
    'U-0008',
    'U-0011',
    'U-0012',
    'U-0014',
    'U-0017',
    'U-0019',
    'U-0020',
    'U-0023',
    'U-0098',
    'U-0178',
    'U-0180',
    'U-0181',
    'U-0183',
    'U-0184',
    'U-0185',
    'U-0186',
    'U-0193',
    ]
  cache = read_cache()
  try:
    main(interviews)
  finally:
    write_cache()


