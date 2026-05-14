"""
    Program odpowoada za przefiltrowanie zbioru poprzez analize statystyczną srodka geometrycznego pupalcji klasy.
    Na podstawie parametru podobieństwa odrzucane zostają nie pasujaće chumry punktów

"""

from data.project_values import *
from src.func.analyzing_tool import filter_RP
from src.func.special import JSON, NPY

import numpy as np
from numpy.typing import NDArray


from typing import Dict, Sequence, List, Tuple

def acctivate_FPR(
            LABEL_array: NDArray[str],
            POINTS_array: NDArray[np.float64],
            class_label_counter: Dict[str, int],
            threshold: float  = THRESHOLD,
            FLAG_save: bool = True,
            name_LABEL_array: str = "FPR_" + NPY.LABEL,
            name_POINTS_array: str = "FPR_" + NPY.POINTS,
            name_counter: str = "FPR_" + JSON.class_label_counter,
        )-> Tuple[NDArray[np.float64], NDArray[np.float64], Dict[str, int]]:

    LOG.print(f"\n[PROC] Start processing FPR of all class labels")

    FPR_class_label_counter: Dict[str, int] = {k: 0 for k in class_label_counter.keys()}
    FPR_LABEL_array: NDArray[np.float64] | None = None
    FPR_POINTS_array: NDArray[np.float64] | None = None

    start_class_label_index: int = 0


    for lb in class_label_counter:

        # if lb != 'fist':
        #     start_class_label_index += class_label_counter[lb]
        #     continue

        LOG.print(f".[INFO] FPR label: {lb}")

        rows = slice( start_class_label_index, start_class_label_index+class_label_counter[lb], 1  )

        start_class_label_index += class_label_counter[lb]

        lbarr = LABEL_array[rows]
        ptarr = POINTS_array[rows, :]

        #filtracja i zwrot
        # stack_lbarr, stack_ptarr = lbarr, ptarr
        stack_lbarr, stack_ptarr, count = filter_RP(lbarr, ptarr, threshold=threshold)

        FPR_class_label_counter[lb] = count

        if FPR_LABEL_array is None:
            FPR_LABEL_array = stack_lbarr
        else:
            FPR_LABEL_array = np.concatenate( [FPR_LABEL_array, stack_lbarr], axis=0 )

        if FPR_POINTS_array is None:
            FPR_POINTS_array = stack_ptarr
        else:
            FPR_POINTS_array = np.concatenate( [FPR_POINTS_array, stack_ptarr], axis=0  )

        LOG.print(f".[INFO] FPR proccesesd {stack_lbarr.shape}, {stack_ptarr.shape}, {FPR_LABEL_array.shape}, {FPR_POINTS_array.shape}")

    LOG.print(f".[INFO] End processing of all class labels")

    NPY.save( name_LABEL_array, FPR_LABEL_array)
    NPY.save( name_POINTS_array, FPR_POINTS_array)
    JSON.save( name_counter, FPR_class_label_counter)

    LOG.print(f"\n[ENDPROC] END processing FPR")

    return FPR_LABEL_array, FPR_POINTS_array, FPR_class_label_counter


if __name__ == '__main__' and 0:

    from src.func.special import JSON, NPY

    L = NPY.load( NPY.LABEL )
    P = NPY.load(NPY.POINTS)
    clc = JSON.load( JSON.class_label_counter )

    acctivate_FPR(L, P, clc)