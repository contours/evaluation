
STRIP_WIDTH = 100
TICK_WIDTH = 5

HEAD = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}" id="svg2">
  <g id="layer1" transform="translate({translate_x},0)">
'''
def header(strips, height):
  return HEAD.format(width=strips*STRIP_WIDTH+5, height=height, translate_x=TICK_WIDTH)

foot = '''
  </g>
</svg>
'''

PATH = '''
    <path
       d="m {startx},{starty} {movex},{movey}"
       id="{pathid}"
       style="fill:none;stroke:{color};stroke-width:{width};stroke-linecap:{cap};stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:{opacity};stroke-dasharray:{dashes};stroke-dashoffset:0" />
'''
def line(strip_index, strip_id, y, length=1, 
         color='#000000', opacity='1', dashed=False):
  return PATH.format(
    startx=strip_index*STRIP_WIDTH,
    starty=y,
    movex=length*STRIP_WIDTH,
    movey=0,
    color=color,
    width=1,
    cap='square',
    opacity=opacity,
    dashes=('3, 3' if dashed else 'none'),
    pathid='{}-{}'.format(strip_id, y))

def tick(y, color='#000000'):
  return PATH.format(
    startx=-TICK_WIDTH,
    starty=y,
    movex=TICK_WIDTH,
    movey=0,
    color=color,
    width=0.5,
    cap='square',
    opacity='1',
    dashes='none',
    pathid='tick-{}'.format(y))

def highlight(y, length, color='#00ff00'):
  return PATH.format(
    startx=-TICK_WIDTH/2.0,
    starty=y,
    movex=0,
    movey=length,
    color=color,
    width=TICK_WIDTH,
    cap='butt',
    opacity='1',
    dashes='none',
    pathid='highlight-{}'.format(y))

LABEL = '''
  <g transform="translate({x},{y})">
    <rect width="{width}" height="8" rx="5" ry="5" x="0" y="-4"
       style="color:#000000;fill:#ffffff;stroke:#000000;stroke-width:0.3;" />
    <text x="3" y="2" style="font-size:6px;font-family:sans-serif">{text}</text>
  </g>
'''
def label(strip_index, y, text):
  return LABEL.format(
    x=strip_index*STRIP_WIDTH,
    y=y,
    text=str(text),
    width=4*len(str(text))+4)

