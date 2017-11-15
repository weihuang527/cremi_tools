from __future__ import print_function
import os
from subprocess import call

import vigra
import numpy as np
from cremi import Volume
from cremi.io import CremiFile

# TODO need proper offsets
offsets = {
    # value from Stephan's original script:
    'A+': (37, 1176, 955),
    # which is
    #   my orignal crop (23, 1060, 839) for sample A+
    #   plus context padding (14, 116, 116)
    # which is exactly the gt bounding box crop
    'B+': (37, 1076, 1284),
    'C+': (37, 1002, 1165),
}

# offsets for larger volumes
#offsets_test = {
#    'A': (23, 1060, 839),
#    'B': (23, 960, 1168),
#    'C': (23, 886, 1049),
#}

# TODO find correct values !
#offsets_train = {
#    'A': (23, 832, 814),
#    'B': (23, 960, 1284),
#    'C': (23, 1002, 1165),
#}


def backalign_segmentation(sample, segmentation, out_file, key='volmes/labels/neuron_ids'):

    # if we get a segmentation, we need to write it to a temp file
    cwd = os.getcwd()
    if isinstance(segmentation, np.ndarray):
        seg_path = os.path.join(cwd, 'tmp1.h5')
        vol_temp = Volume(segmentation, resolution=(40., 4., 4.))
        cremi_temp = CremiFile(seg_path, 'w')
        cremi_temp.write_neuron_ids(vol_temp)
        cremi_temp.close()
    elif isinstance(segmentation, str):
        assert os.path.exists(segmentation), segmentation
        seg_path = segmentation
    else:
        raise RuntimeError("Unsupported Input type!")

    tmp_file2 = os.path.join(cwd, 'tmp2.h5')

    exe_file = "transformations/deform-0.0.1-SNAPSHOT.jar"
    trafo_file = "transformations/sample_%s.transforms.json" % sample

    this_dir = os.path.dirname(os.path.realpath(__file__))
    exe_file = os.path.join(this_dir, exe_file)
    trafo_file = os.path.join(this_dir, trafo_file)

    source_offset = "%d,%d,%d" % offsets[sample]
    call(["java", "-Xmx6g", "-cp", exe_file, "org.janelia.saalfeldlab.deform.DeformFromAligned",
          "-j", seg_path,  # this is the input file
          "-l", key,
          # offset in input
          # (due to crop of aligned volume by me)
          "--labelssourceoffset", source_offset,
          "-o", out_file,  # this is the output file
          "-t", trafo_file,
          # offset in output
          # (begin of label region in original padded volume, same for all
          # samples)
          "--targetoffset", "37,911,911",
          # interval in which transformations are defined (same for all
          # samples)
          "--transformsize", "200,3072,3072",
          # output size
          "--targetsize", "125,1250,1250",
          # mesh cell size
          "-c", "64"])

    if isinstance(segmentation, np.ndarray):
        os.remove(segmentation)
