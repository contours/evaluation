
STRIP_WIDTH = 100

HEAD = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}" id="svg2">
  <g id="layer1">
'''
def header(strips, height):
  return HEAD.format(width=strips*STRIP_WIDTH, height=height)

foot = '''
  </g>
</svg>
'''

PATH = '''
    <path
       d="m {startx},{starty} {length},0"
       id="{pathid}"
       style="fill:none;stroke:{color};stroke-width:1;stroke-linecap:square;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:{opacity};stroke-dasharray:{dashes};stroke-dashoffset:0" />
'''
def line(strip_index, strip_id, y, length=1, 
         color='#000000', opacity='1', dashed=False):
  return PATH.format(
    startx=strip_index*STRIP_WIDTH,
    starty=y,
    length=length*STRIP_WIDTH,
    color=color,
    opacity=opacity,
    dashes=('3, 3' if dashed else 'none'),
    pathid='{}-{}'.format(strip_id, y))

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

