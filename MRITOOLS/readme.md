# MRITOOLS
This package consists of [Nodes](/MRITOOLS/Nodes), [Workflows](/MRITOOLS/Workflows) and [Utils](/MRITOOLS/Utils)

## [Nodes](/MRITOOLS/Nodes)
Nodes are self contained functions for data-preprocessing, including:
1. Conversion from DICOM to nifti (CONVERTER)
2. Slice timing correction (SLICETIMER)
3. Motion correction (MCORRECTOR)
4. Brain extraction (EXTRACTER)
5. Spatial smoothing (SMOOTHER)
6. High-pass temporal filtering (HPFILTER)

### General usage example:

Executing the spatial smoothing node:
```python
from MRITOOLS.Nodes import SMOOTHER
SMOOTHER()
```

## [Workflows](/MRITOOLS/Workflows)

Workflows are a series of inter-connected nodes that form a full-processing pipeline, including:
1. Pre-processing of functional volumes (FUNCPIPE)
2. Registration/ normalisation (NORMPIPE)
3. Level 1 analysis of functional volume, using the example data (L1PIPE)
4. Render statistics onto MNI brain/ structural volume (RENDERPIPE).

### General usage example:

Executing the functional pre-processing workflow:
```python
from MRITOOLS.Workflows import FUNCPIPE
FUNCPIPE()
```

## [Utils](/MRITOOLS/Utils)

Utils are a set of functions that are not necessarily part of the pre-processing pipeline but are convenient for data manipulation/ plotting (cropping volumes, printing nifti headers). These are under development. Details are provided in the readme.
