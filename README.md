```
usage: filter.py [-h] filename coders

Filter a segmentation file to only include the specified coders.

positional arguments:
  filename    name of the JSON segmentation file
  coders      only include specified coders

optional arguments:
  -h, --help  show this help message and exit
```
```
usage: gold.py [-h] [-n] filename

Generates a 'gold' segmentation by majority vote.

positional arguments:
  filename    name of the JSON segmentation file

optional arguments:
  -h, --help  show this help message and exit
  -n, --near  count near agreement when majority voting
```
```
usage: mean_pi.py [-h] filename gold

Calculate mean π against a gold segmentation.

positional arguments:
  filename    name of the JSON segmentation file
  gold        name of the gold segmentation file

optional arguments:
  -h, --help  show this help message and exit
```
```
usage: near_agreement_alpha.py [-h] [-c CODERS] [--reference REFERENCE]
                               filename

Calculates near segmentation agreement using Krippendorf's α.

positional arguments:
  filename              name of the JSON segmentation file

optional arguments:
  -h, --help            show this help message and exit
  -c CODERS, --coder CODERS
                        only include these coders (must have 2 or more)
  --reference REFERENCE
                        name of the reference annotator used to calculate k
```
```
usage: near_agreement_multipi.py [-h] [--reference REFERENCE] filename

Calculates near segmentation agreement using Fleiss’s multi-π.

positional arguments:
  filename              name of the JSON segmentation file

optional arguments:
  -h, --help            show this help message and exit
  --reference REFERENCE
                        name of the reference annotator used to calculate k
```
```
usage: nullseg.py [-h] filename

Produce a null (no boundaries) segmentation for comparison purposes.

positional arguments:
  filename    name of the JSON segmentation file

optional arguments:
  -h, --help  show this help message and exit
```
```
usage: plots.py [-h] filename svg

positional arguments:
  filename    name of the JSON segmentation file
  svg         file to save the SVG figure as

optional arguments:
  -h, --help  show this help message and exit
```
```
usage: randomseg.py [-h] filename

Produce a random segmentation for comparison purposes.

positional arguments:
  filename    name of the JSON segmentation file

optional arguments:
  -h, --help  show this help message and exit
```
```
usage: strict_agreement.py [-h] [-c CODERS] [-e filename] filename

Calculates strict segmentation agreement.

positional arguments:
  filename              name of the JSON segmentation file

optional arguments:
  -h, --help            show this help message and exit
  -c CODERS, --coder CODERS
                        only include specified coders
  -e filename, --evaluate filename
                        name of a segmentation file to evaluate
```
```
usage: visualize.py [-h] [-c filename:color] [-o DIR] filename

Produce SVG visualizations of segmentations.

positional arguments:
  filename              name of the JSON segmentation file

optional arguments:
  -h, --help            show this help message and exit
  -c filename:color, --compare filename:color
                        name of a file with a segmentation to overlay for
                        comparison, and a color to use
  -o DIR, --output DIR  directory to write SVG files to
```
