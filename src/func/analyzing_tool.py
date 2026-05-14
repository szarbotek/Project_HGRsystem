
import numpy as np
from numpy.typing import NDArray

from sklearn.model_selection import train_test_split

from typing import Literal, Tuple, Union, List, Any, Dict

# from tensorflow.python.ops.gen_math_ops import mean

def landmark2array(landmark) -> NDArray[np.float64]:
    """
        Funkcja zamienia landmark na tablice NParray
    """
    points = []
    for lm in landmark:
        points.extend([lm.x, lm.y, lm.z])

    return np.array(points, dtype=np.float64)

def get_landmark_site( result, index:int=0 )->Tuple[ Any, str ]:
    return result.hand_landmarks[index], result.handedness[index][0].category_name

def select_higher_gesture( result ) -> Union[ Tuple[NDArray[np.float64], Literal["Left", "Right"]], Tuple[None, None] ]:
    """
        Funkcja odnajduje gest położony wyżej na zdjęciu

    :param result:
    :return: zwracana jest landmark oraz informacje o stronie ręki
    """
    min_Y = None
    index:int = 0

    # wyszykanie minimalnego Y dla instancji
    for i, landmark in enumerate(result.hand_landmarks):

        if min_Y is None:
            min_Y = landmark[0].y
        elif min_Y > landmark[0].y:
            min_Y = landmark[0].y
            index = i

    return get_landmark_site( result, index )

def rotYaxis(
            points: NDArray[np.float64],
            angelDeg:float
        )-> NDArray[np.float64]:

    points: NDArray = points.reshape(-1, 3)

    theta = np.radians(angelDeg)

    # rotator do rotacji w płaszyżnie XY
    Rot = np.array([
        [np.cos(theta),    0,   np.sin(theta)],
        [0,                1,   0            ],
        [-np.sin(theta),   0,   np.cos(theta)]
    ])

    points_rotation = (Rot @ points.T).T

    return points_rotation.flatten()


def normalization( points: NDArray[np.float64], site: Literal["Right", "Left"], rotarAngle: float = 0.0,
                    FLAG_translation: bool = True,
                    FLAG_mirror: bool = True,
                    FLAG_scale: bool = True,
                    FLAG_rotation: bool = True) -> NDArray[np.float64]:
    """
        Normalizacja polega na 4 etapach
        1. Translacja w przestrzenie wzgledem WRIST - umieszcenie wszystkich landmarków w jednym punkcie
        2. Mirror przekształaca lewe ręce w prawe
        3. Sklaowanie normalizuje rozmiar do jedności między [0] i [9]
        4. rotacja: wektor [0][9] zostaje obrócony o kąt w płaszczyżnie XY pokrywającej się z punktami
            dotkowo obrót może zostać wykonany z dodatkowym offsetem

    :param points:
    :param site:
    :param FLAG_translation:
    :param FLAG_mirror:
    :param FLAG_scale:
    :param FLAG_rotation:
    :return:
    """

    if not FLAG_translation: return points

    # warstwa pierwasza translacja do origin point ====================================================================

    # normalizacja do origing point we WRIST
    points_translatin = points.reshape(-1, 3)
    WRIST = points_translatin[0,:]
    points_translatin -= WRIST

    if not FLAG_mirror: return points_translatin.flatten()

    # warstwa druga mirror Left -> Right <- Right =====================================================================

    if site not in ("Right", "Left"): raise ValueError("[ERR] Answer must be 'Right' or 'Left' ")

    # przełozenie punktów na prawą stronę
    if site == "Left":
        points_mirror = points_translatin *  np.array([-1, 1, 1])
    else:
        points_mirror = points_translatin

    if not FLAG_scale: return points_mirror.flatten()

    # warstwa trzecia skalowanie ======================================================================================

    vector = points_mirror[0,:] - points_mirror[9,:]
    a = 1 / np.linalg.norm( vector  )

    points_scale = points_mirror * a

    if not FLAG_rotation: return points_scale.flatten()
    # warstwa czwarta rotacja =========================================================================================

    W = np.array( points_scale[0,:] )
    M = np.array( points_scale[9,:] )
    W[2] = 0
    M[2] = 0

    Y = np.array([0,-1,0])

    MW = M - W

    dot_product = np.dot(MW, Y)
    norm_MW = np.linalg.norm( MW )
    norm_Y = np.linalg.norm( Y )

    # kąt miedzy wektorami
    cos_theta = dot_product / (norm_MW * norm_Y)

    # zakres
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    theta = -np.arccos(cos_theta)
    theta =  np.radians( np.degrees(theta)+rotarAngle )

    # rotator do rotacji w płaszyżnie XY
    Rot_z = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])

    points_rotation = (Rot_z @ points_scale.T).T

    return points_rotation.flatten()


def filter_RP(
            labels: NDArray[str],
            population: NDArray[np.float64],
            threshold: float = 0.25
        ) -> Tuple[  NDArray[str],  NDArray[np.float64], int ]:

    """
        Funkcja przeprowadza filtrację za pomocą analizy rozkładu normalnego


    :param population:
    :param labels:
    :param threshold: określa poziom flitracji (okolice -2 bliskie 0)
    :return:
    """

    if len(population) ==  1:
        return labels, population, 1

    MEAN: List[NDArray[np.float64]] = []

    # środek geometryczy obecnej populaci
    colx = slice(0, 63, 3)
    coly = slice(1, 63, 3)

    x_GC: float = np.mean( population[:, colx])
    y_GC: float = np.mean( population[:, coly])

    GC = np.array([x_GC, y_GC]).reshape(2, 1)

    # środek geometryczny instancji

    x_means = np.mean(population[:, colx], axis=1)
    y_means = np.mean(population[:, coly], axis=1)

    MEAN = np.stack([x_means, y_means], axis=1).reshape(-1, 2, 1)

    Q = GC - MEAN
    DISTANCE = np.linalg.norm(Q, axis=(1, 2))

    D = np.array(DISTANCE)
    D_scores = (D - np.mean(D)) / np.std(D, ddof=1)

    # for i in range(len(population)):
    #     xmm = np.mean( np.mean( population[i, colx]) )
    #     ymm = np.mean( np.mean( population[i, coly]) )
    #     MEAN.append( np.array( [xmm, ymm]) )
    #
    # RV = []
    #
    # # odkległość miedzy środkeigm geomtrycznym globalnym a lokalnymi
    # DISTANCE: List[NDArray[np.float64]]  = []
    # for i, M in enumerate(MEAN):
    #     Q = GC - M
    #     RV.append( GC - M )
    #     DISTANCE.append( np.linalg.norm(GC - M) )


    # normalizacja rozkłąd Z-scrore normalization T-studenta
    # D = np.array(DISTANCE)
    # D_scores = (D - np.mean(D)) / np.std(D, ddof=1)


    # przenoszenie instancji znajdujących sie w okrełśonym zakresie (bliskim sąsiedwie)
    ACCEPT_population: NDArray[np.float64] | None = None
    ACCEPT_laybels: NDArray[str] | None = None

    buff_: List[str] = []

    count: int = 0

    for index, D_sample in enumerate(D_scores):
        if  D_sample <= threshold:

            count +=1
            if ACCEPT_population is None:
                ACCEPT_population = population[index:index+1,:]
            else:
                ACCEPT_population = np.concatenate([ACCEPT_population, population[index:index+1,:]], axis=0)

            buff_.append( labels[index] )

    ACCEPT_laybels = np.array( buff_ )

    return ACCEPT_laybels, ACCEPT_population, count

#
# def filter_RP2(  population: List[NDArray[np.float64]],
#                         laybels: List[str],
#                         threshold: float = 0.25
#                         ) -> Tuple[List[NDArray[np.float64]], List[str]]:
#     """
#         Funkcja przeprowadza filtrację za pomocą analizy rozkładu normalnego
#
#
#     :param population:
#     :param laybels:
#     :param threshold: określa poziom flitracji (okolice -2 bliskie 0)
#     :return:
#     """
#
#     assert len(population) >= 1, ValueError("[ERR] Population must have at least one row")
#
#     MEAN: List[NDArray[np.float64]] = []
#
#     X_CENTER: List[float] = []
#     Y_CENTER: List[float]  =[]
#
#     # wyznaczenie środków geometrycznych poszcególnych instancji
#     for LParray in population:
#
#         X_MEAN: float = np.mean( LParray[0:-1:3] )
#         Y_MEAN: float = np.mean( LParray[1:-1:3] )
#
#         X_CENTER.append( X_MEAN )
#         Y_CENTER.append( Y_MEAN )
#
#         MEAN.append( np.array([X_MEAN, Y_MEAN]) )
#
#     # środek geometryczny całej populacji
#     X_CENTER: float = np.mean( X_CENTER )
#     Y_CENTER: float = np.mean( Y_CENTER )
#
#     C = ( np.array([ X_CENTER, Y_CENTER]) )
#
#     DISTANCE: List[float] = []
#     for M in MEAN: DISTANCE.append( np.linalg.norm( C - M ) )
#
#     # normalizacja rozkłąd Z-scrore normalization T-studenta
#     D = np.array(DISTANCE)
#     D_scores = (D - np.mean(D)) / np.std(D)
#
#     ACCEPT_population = []
#     ACCEPT_laybels = []
#
#
#     # przepuszczenie landmarków znajdujących się w bliskim sąsiedztwie
#     for index, D_sample in enumerate( D_scores):
#         if  D_sample <= threshold:
#             ACCEPT_population.append( population[index] )
#             ACCEPT_laybels.append( laybels[index] )
#
#     INFO_elimination = len( population ) - len( ACCEPT_population )
#
#     return ACCEPT_population, ACCEPT_laybels, INFO_elimination

def data_separate(
            LABEL_array: NDArray[str], POINTS_array: NDArray[np.float64],
            class_label_counter: Dict[str, int]
        )->Tuple[ NDArray[str], NDArray[np.float64], NDArray[str], NDArray[np.float64], NDArray[str], NDArray[np.float64]  ]:


    train_labels: NDArray[str] | None = None
    train_points: NDArray[np.float64] | None = None

    test_labels: NDArray[str] | None = None
    test_points: NDArray[np.float64] | None = None

    valid_labels: NDArray[str] | None = None
    valid_points: NDArray[np.float64] | None = None

    #  test 15%
    rest_points, test_points, rest_labels, test_labels = train_test_split(
        POINTS_array,
        LABEL_array,
        test_size=0.15,
        stratify=LABEL_array,
        random_state=42
    )

    #  train 80%, ️validation 15%
    train_points, valid_points, train_labels, valid_labels = train_test_split(
        rest_points,
        rest_labels,
        test_size=0.1765,
        stratify=rest_labels,
        random_state=42
    )

    return train_labels, train_points, test_labels, test_points, valid_labels, valid_points


if __name__ == '__main__':

    def visual_filter_population(population: List[NDArray[np.float64]],
            laybels: List[str],
                    threshold: float = 0.25
                    ) -> Tuple[List[NDArray[np.float64]], List[str]]:

        assert len(population) >= 1, ValueError("[ERR] Population must have at least one row")

        from matplotlib import pyplot as plt

        plt.figure(figsize=(6, 6))

        MEAN: List[NDArray[np.float64]] = []

        X_CENTER: List[float] = []
        Y_CENTER: List[float] = []

        for LParray in population:
            X_MEAN: float = np.mean(LParray[0:-1:3])
            Y_MEAN: float = np.mean(LParray[1:-1:3])

            X_CENTER.append(X_MEAN)
            Y_CENTER.append(Y_MEAN)

            MEAN.append(np.array([X_MEAN, Y_MEAN]))

            plt.scatter(x=LParray[0:-1:3], y=LParray[1:-1:3], c=np.random.rand(3), s=5)

        X_CENTER: float = np.mean(X_CENTER)
        Y_CENTER: float = np.mean(Y_CENTER)

        C = (np.array([X_CENTER, Y_CENTER]))

        DISTANCE: List[float] = []
        for M in MEAN:
            DISTANCE.append(np.linalg.norm(C - M))

        # normalizacja rozkłąd Z-scrore normalization T-studenta
        D = np.array(DISTANCE)
        D_scores = (D - np.mean(D)) / np.std(D)
        D_accept = []

        for i, ddd in enumerate(D_scores):

            plt.scatter(x=MEAN[i][0], y=MEAN[i][1], c='blue', s=25)

            if ddd <= -0.25:
                plt.scatter(x=MEAN[i][0], y=MEAN[i][1], c='red', s=25)
                D_accept.append(ddd)

        plt.scatter(x=X_CENTER, y=Y_CENTER, c='black', s=80)

        D_accept = np.array(D_accept)

        plt.title(f"Rozdkład 400 losowo wygenerowancych chmur punktów")
        plt.show()

        # Histogram
        plt.figure(figsize=(10, 6))

        bins = np.linspace(D_scores.min(), D_scores.max(), 20)

        plt.hist(D_scores, bins=bins, density=False, alpha=0.5, color='blue', label='D_scores')
        plt.hist(D_accept, bins=bins, density=False, alpha=0.5, color='red', label='D_scores')

        # x_axis = np.linspace(-4, 4, 100)
        # plt.plot(x_axis, norm.pdf(x_axis, 0, 1), 'r', lw=2, label='Wzorcowy Gauss')

        plt.axvline(x=-0.25, color='red', linestyle='-', linewidth=2)

        from matplotlib.ticker import MultipleLocator

        ax = plt.gca()
        ax.xaxis.set_major_locator(MultipleLocator(0.5))

        plt.title(f"Histogram 400 populacji chmur punktów")
        plt.grid(True, axis='x', alpha=0.3)
        plt.show()


    # https://www.geeksforgeeks.org/data-analysis/z-score-normalization-definition-and-examples/

    visual_filter_population( np.random.rand(400, 63), "none", 0.5 )