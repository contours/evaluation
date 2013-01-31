```
usage: strict_agreement.py [-h] [-k] filename

Calculates strict segmentation agreement.

positional arguments:
  filename     name of the JSON segmentation file

optional arguments:
  -h, --help   show this help message and exit
  -k, --kappa  also calculate multi-κ agreement and bias
```  
```
usage: near_agreement_alpha.py [-h] [--reference REFERENCE] filename

Calculates near segmentation agreement using Krippendorf's α.

positional arguments:
  filename              name of the JSON segmentation file

optional arguments:
  -h, --help            show this help message and exit
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
usage: gold.py [-h] [-n] filename

Generates a 'gold' segmentation by majority vote.

positional arguments:
  filename    name of the JSON segmentation file

optional arguments:
  -h, --help  show this help message and exit
  -n, --near  count near agreement when majority voting
```
```
usage: visualize.py [-h] [-o DIR] [-g GOLD] filename

Produce SVG visualizations of segmentations.

positional arguments:
  filename              name of the JSON segmentation file

optional arguments:
  -h, --help            show this help message and exit
  -o DIR, --output DIR  directory to write SVG files to
  -g GOLD, --gold GOLD  name of a gold segmentation file
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
