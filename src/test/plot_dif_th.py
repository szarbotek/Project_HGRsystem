

from creatMLP.layerFPR import acctivate_FPR

from  plot import visual2d
from func.special import NPY, JSON

L = NPY.load(NPY.LABEL)
P = NPY.load(NPY.POINTS)
clc = JSON.load(JSON.class_label_counter)

for i, threshold in enumerate([-0.5, 0, 0.25, 0.5, 0.75, 1.0, 1.5, 10.0]):

    _L, _P, _clc = acctivate_FPR(L, P, clc, threshold=threshold, )

    fd = f"threshold_{threshold}"
    visual2d.distribution(_clc, FLAG_save=True, name="DST_FPR", target_folder=fd )
    visual2d.distribution_of_class_label_points(_L, _P, _clc, target_folder=fd )