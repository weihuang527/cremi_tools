import vigra

sys.path.append('../..')
import cremi_tools.viewer.volumina as volumina
from cremi_tools.segmentation_comparison import SegmentationComparison


def compare_segs():
    raw_path = '/home/consti/Work/data_neuro/knott_data/testset/knott_test_raw.h5'
    seg_path = '/home/consti/Work/data_neuro/knott_data/testset/knott_test_seg.h5'
    mc0_path = '/home/consti/Work/data_neuro/knott_data/results/multicut_paper_cut_cc.h5'
    mc1_path = '/home/consti/Work/data_neuro/knott_data/results/multicut.h5'

    seg = vigra.readHDF5(seg_path, 'data').astype('uint32', copy=False)
    mc0 = vigra.readHDF5(mc0_path, 'data').astype('uint32', copy=False)
    mc1 = vigra.readHDF5(mc1_path, 'data').astype('uint32', copy=False)

    seg_comparison = SegmentationComparison(seg)
    edge_vol = seg_comparison.edge_difference_volume(mc0, mc1)

    raw = vigra.readHDF5(raw_path, 'data')
    volumina.view([raw, seg, mc0, mc1, edge_vol],
                  ['raw', 'seg', 'mc-niko', 'mc', 'edge-diff'])


if __name__ == '__main__':
    compare_segs()
