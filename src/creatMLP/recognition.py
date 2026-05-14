"""
    Program na podsawie dostarczonej struktury etykiet, otwiera model MEDIAPIPE hand_landmark.task i pobiera landmark
    dla każdego wykrytego gestu.

    Każdy gest jest z osobna normalizowany.

    Cała populacja gestu jest oddawana analizie redukcji szumów

    Dane są zapisywane w 2 tablicach z podziałem na Etykiety i Dane (1,63 na jedną próbkę)
"""

import csv

from data.project_values import *
from src.func.analyzing_tool import select_higher_gesture, get_landmark_site, landmark2array, normalization, rotYaxis
from src.func.special import JSON, NPY, CSV

import mediapipe as mp
from mediapipe.tasks import python as mp_python

import numpy as np
from numpy.typing import NDArray

from typing import Dict, Sequence, List, Tuple

def generate_array_of_class_data(
            class_label_set: Dict[str, Sequence[str]],
            limit_per_class: int = LIMIT_PER_CLASS,
            name_LABEL_array: str = NPY.LABEL,
            name_POINTS_array: str = NPY.POINTS,
            flag_normalization = FALG_NORMALIZATION,
        )-> Tuple[NDArray[np.float64], NDArray[np.float64], Dict[str, int]]:
    """
        Funkcja wykorzystuje model handmark_landmarks.task do przeprocesowania zdjeć na dane numeryczne

        Dane numeryczne są poddawane normalizacji: pozycji, rozmiaru, i odbicia.

        Wy wyniku działa sa generowane 2 tablice NDarray odpowidnio dla populacji chmur punktów w stosie Nx63
        i zbiór klas etykiet Nx1

    """

    assert isinstance(class_label_set, dict), TypeError("<ERR> Wrong data type (Dict)")
    assert all([isinstance(l, str) for l in class_label_set]), TypeError("<ERR> Wrong type of kayes (str)")
    assert all([isinstance(v, Sequence) for v in class_label_set.values()]), TypeError(
        "<ERR> Wrong type of values (List)")
    assert all(
        isinstance(v, str)
        for l in class_label_set
        for v in class_label_set[l]
    ), TypeError("<ERR> Wrong type of path (List[str])")

    LOG.print(f"\n[PROC] Start generating table of landmarks points")

    save_path = PATH.data_numerical
    model_path = PATH.hand_landmark

    class_label_counter: Dict[str, int] = { k: 0 for k in class_label_set.keys()}

    base_options = mp_python.BaseOptions(
        model_asset_path=model_path,
        delegate=mp_python.BaseOptions.Delegate.CPU  # GPU
    )

    # https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker?hl=pl
    options = mp_python.vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        min_hand_presence_confidence=0.35,
        min_hand_detection_confidence=0.35,
        min_tracking_confidence=0.5,
    )

    LABEL: List[str] = []
    POINTS: List[NDArray] = []

    try:
        # uruchomienie instancji modelu
        with mp_python.vision.HandLandmarker.create_from_options(options) as recognizer:
            LOG.print(f".[INFO] Model opened correctly")

            clb_len = len(class_label_set)

            # opczytywanie etykiet klas
            for index, (lb, samples) in enumerate(class_label_set.items()):

                LOG.print(f".[INFO] {LOG.counter(index, clb_len)} Recognizing class label: {lb}")

                CT00: int = 0

                # odczytywanie kolejnych próbek
                for s in samples:
                    # licznik przetworzonych próbek
                    if CT00 >= limit_per_class: break
                    else: CT00 += 1

                    result = None
                    landmark, site = None, None

                    LParray: NDArray[np.float64] = None
                    norm_LParray: NDArray[np.float64] = None

                    # odczyt zdjecia
                    try:
                        assert os.path.exists( s ), FileExistsError

                        reco_image = mp.Image.create_from_file( s )

                        # przprocesowanie zdjęcia przez model
                        result = recognizer.detect( reco_image )
                    except Exception as e:
                        LOG.print(f"<ERR> Image has recognizon problem: {e}")

                    # przekształacanie wyniku
                    try:
                        if len(result.hand_landmarks) >= 2:
                            landmark, site = select_higher_gesture( result )

                        elif len(result.hand_landmarks) == 1:
                            landmark, site = get_landmark_site( result )
                        else:
                            continue

                        LParray= landmark2array(landmark)

                        norm_LParray = normalization( LParray, site, **flag_normalization )
                    except Exception as e:
                        LOG.print(f"<ERR> Analyze problem: {e}")

                    LABEL.append( lb )
                    POINTS.append( norm_LParray )
                    class_label_counter[lb] += 1

                    pass
            else:
                LOG.print(f".[INFO] All classes were recognized")
    except Exception as e:
        LOG.print(f"<ERR> Model cannot be initialize: {e}")
        return

    LOG.print(f".[INFO] Recognizion end successfully")

    LABEL_array: NDArray = np.array(LABEL)
    POINTS_array: NDArray = np.array(POINTS)

    LOG.print(f".[INFO] Final shape: \n\tLabel: {LABEL_array.shape}, \n\tPoints: {POINTS_array.shape}")

    #zapisywanie tablicy wynikowej i countera
    NPY.save(name_LABEL_array, LABEL_array)
    NPY.save(name_POINTS_array, POINTS_array)
    JSON.save(JSON.class_label_counter, class_label_counter)

    LOG.print(f"[ENDPROC] End processing")

    return LABEL_array, POINTS_array, class_label_counter


def add_gesture_thumb_index_inv(
            LABELS_array: NDArray[int],
            POINTS_array: NDArray[int],
            class_label_counter: Dict[str, int],
            angelDeg: int,
        ) -> Tuple[NDArray[np.float64], NDArray[np.float64], Dict[str, int], NDArray[np.float64], NDArray[np.float64], Dict[str, int]]:

    LOG.print(f"\n[PROC] Adding thumb index inv")

    retL: List[NDArray[np.float64]] = []
    retP: NDArray[np.float64] | None = None

    clc_w = {
        "thumb_index_inv": 0
    }

    for index, lb in enumerate(LABELS_array):

        if lb == "thumb_index":
            clc_w["thumb_index_inv"] += 1

            pth = POINTS_array[index,:]

            pth_inv = rotYaxis(pth, -angelDeg)

            if retP is None:
                retP = pth_inv
            else:
                retP = np.row_stack( (retP, pth_inv) )

            retL.append( "thumb_index_inv" )

    retL = np.array(retL)

    LOG.print(f".[INFO] Find labels: {retL.shape}, points {retP.shape} ")

    LABELS_array  = np.concatenate( (LABELS_array, retL)   )
    POINTS_array  = np.concatenate( (POINTS_array, retP)   )
    class_label_counter.update( clc_w )

    NPY.save( "modif_"+NPY.LABEL, LABELS_array )
    NPY.save( "modif_"+NPY.POINTS, POINTS_array )
    JSON.save(JSON.class_label_counter, class_label_counter)

    CSV.save( "modif_"+NPY.LABEL, LABELS_array )
    CSV.save( "modif_"+NPY.POINTS, POINTS_array )

    LOG.print(f"\n[ENDPROC] End processing: thumb index inv")

    return LABELS_array, POINTS_array, class_label_counter, retL, retP, clc_w


if __name__ == '__main__' and 0:

    IK = 10
    ph = r"P:\INZ\ProjectPD\assets\image\model_training\call\{}.jpg"
    dt = {"call":
            [  ph.format(i)
                for i in range(1,IK)
            ]
        }
    print(dt)

    generate_array_of_class_data(
        dt,
        IK
    )

if __name__ == '__main__' and 0:

    from src.func.special import NPY, JSON

    L = NPY.load( NPY.LABEL )
    P = NPY.load( NPY.POINTS )
    clc = JSON.load( JSON.class_label_counter )

    *_, nL, nP, nclc = add_gesture_thumb_index_inv(L, P, clc)

    from plot import visual2d
    visual2d.distribution_of_class_label_points( nL, nP, nclc  )
