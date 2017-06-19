# MRITOOLS
This package consists of [Nodes](/MRITOOLS/Nodes) and [Workflows](/MRITOOLS/Workflows)

## [Nodes](/Nodes)
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

## [Workflows](/Workflows)

Workflows are a series of inter-connected nodes that form a full-processing pipeline, including:
1. Pre-processing of functional volumes (FUNCPIPE)
2. Registration/ normalisation (STRUCTPIPE)
3. Level 1 analysis of functional volume (L1PIPE)

### General usage example:

Executing the functional pre-processing workflow:
```python
from MRITOOLS.Workflows import FUNCPIPE
FUNCPIPE()
```
