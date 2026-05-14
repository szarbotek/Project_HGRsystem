"""
    Funkcja pozwala na dodawanie rokzładów dystrybucji:
        etykiet klas
        rozkłąd mapy chmury punktów etykiety
"""


import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from data.project_values import *

from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE

import numpy as np
from numpy.typing import NDArray

from typing import Dict, Union, Sequence, Tuple

_tdata = Union[
    Dict[str, int],
    Sequence[
        Union[Sequence[str], Sequence[int]]
    ]
]

def distribution( data: _tdata,
            FLAG_save:bool = True,  name: str = PATH.random_key(),
            target_folder: str = PATH.distbt, extension: str = 'jpg',
            FLAG_abc: bool = True, FLAG_show: bool = False, title:str = "Distribution of data")->None:
    """
        Funkcja rysuje wykres rozkładu zmiennych

    :param data: dane etykiet i liczebności
    :param extension: rozszerzenie zapisu
    :param FLAG_abc: sortowanie alfabetyucznie
    """
    LOG.print(f"[PLOT] Drawing distribution of {name}")

    # przygotowanie danych
    if isinstance(data, dict):
        pass
    elif isinstance(data, Sequence):
        assert isinstance(data[0], Sequence) and isinstance(data[1], Sequence), TypeError("Not Seqentional")
        assert any(isinstance(d, str) for d in data[0]), TypeError("Required Sequence[str]")
        assert any(isinstance(d, int) for d in data[1]), TypeError("Required Sequence[int]")
        data = {k: v for k, v in zip(data[0], data[1]) }

    x: Sequence[str] = None
    y: Sequence[int] = None

    # aktywne sortowanie
    if FLAG_abc:
        x_sorted = sorted(data.keys())
        y = [data[k] for k in x_sorted]
        x = [k.replace("_", " ") for k in data.keys()]
    else:
        x, y = data.items()

    plt.figure(figsize=(15, 10))
    sns.barplot(x=x, y=y, hue=y, palette='viridis', legend=False)
    plt.title(title)
    plt.xticks(rotation=90)

    # tryb zapis lub wyświetlanie wykresu
    if FLAG_save:

        save_path = os.path.join( PATH.axes, target_folder)

        if not os.path.exists(save_path):
            os.mkdir(save_path)
            LOG.print(f".[INFO] Make directory {save_path}")

        fl_save_path =  os.path.join( save_path, PATH.get_file(name, extension))

        plt.savefig(fl_save_path, format=extension, dpi=300)
        LOG.print(f"=[SAVE] Save file: {fl_save_path} ")
    else:
        if FLAG_show:
            plt.show()
        else:
            pass
    plt.close()
    return


def distribution_of_class_label_points(
            LABEL_array: NDArray,
            POINTS_array: NDArray,
            class_label_counter: Dict[str, int],
            target_folder=PATH.distbt, extension: str = "jpg" )->None:
    """
        Funkcja generuje zibór wykresów rozkłądow punktów dla przypisanych etykiet klas.

        : param LABEL_array: zbiór etykiet
        : param POINTS_array: tablica wartości punktów (N x 63)
    """
    LOG.print(f"[PLOT] Drawing distribution of class_label_points")

    save_path = os.path.join( PATH.axes, target_folder)

    if not os.path.exists(save_path):
        os.mkdir(save_path)
        LOG.print(f"=[SAVE] Make directory {save_path}")

    display_characteristic_points: Dict[int, Tuple[str, str]]= {
        0:  ("WRIST",  "#8000ff"),
        4:  ("THUMB",  "#00bde0"),
        8:  ("INDEX",  "#38ff6b"),
        12: ("MIDDLR", "#c4c400"),
        16: ("RING",   "#ff3800"),
        20: ("PINKY",  "#c40038"),
    }

    label_population_finish: int = 0
    plot_label = None

    FLAG_new_plot: bool = False
    save_axes_path: str | None = None

    LABEL_with_endpoint = np.hstack( [LABEL_array, np.nan]  )


    for index, lb in enumerate( LABEL_with_endpoint ):

        if lb != plot_label:

            if FLAG_new_plot:

                # dodanie śrenich punków geometrycznych dla wskazanych punktów charakterystycznych
                for k, v in display_characteristic_points.items():

                    row = slice(index - class_label_counter[plot_label], index, 1)
                    col = k * 3

                    x_cp: float = np.mean( POINTS_array[row, col + 0])
                    y_cp: float = np.mean( POINTS_array[row, col + 1])

                    plt.scatter(x_cp, y_cp, c=v[1], marker='x', s=45, label=v[0])

                # środek geometryczy obecnej populaci
                row = slice(index - class_label_counter[plot_label], index, 1)
                colx = slice(0, 63, 3)
                coly = slice(1, 63, 3)

                x_GC: float = np.mean( POINTS_array[row, colx])
                y_GC: float = np.mean( POINTS_array[row, coly])

                plt.scatter(x_GC, y_GC, c="black", marker='x', s=45, label="geometric center")

                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
                plt.tight_layout()

                save_axes_path = os.path.join(save_path, PATH.get_file(plot_label, extension))

                #zapisanie wykresu
                plt.savefig(save_axes_path, format=extension, dpi=300)
                plt.close()

                FLAG_new_plot = False
                LOG.print(f"=[SAVE] Save plot as: {PATH.get_file(plot_label, extension)} to: {save_axes_path}")

                if index == len(LABEL_array): continue

            FLAG_new_plot = True
            label_population_finish += class_label_counter[lb]
            plot_label = lb

            plt.figure(figsize=(8, 6))
            plt.title( f"Population of {lb}, with {class_label_counter[lb]} sample")
            plt.gca().invert_yaxis()
            plt.grid(True, linestyle='--', alpha=0.6)

            LOG.print(f".[INFO] {LOG.counter(index, label_population_finish)}{[len(LABEL_array)]} Drawing new plot: {lb}")

        x_insp = POINTS_array[index, :][0:-1:3]
        y_insp = POINTS_array[index, :][1:-1:3]

        plt.scatter(x_insp, y_insp, c=range(21), cmap='rainbow', s=5)



def T_SNE(
            LABEL_array: NDArray,
            POINTS_array: NDArray,
            class_label_counter: Dict[str, int],
            perplexity: int,
    ):
    """"
        Funkcja od rysowania rozkładu T-SNE

    """

    LOG.print(f"\n[PROC] Drawing T-SNE")


    # generacja T-SNE
    tsne = TSNE(n_components=2, perplexity=perplexity, learning_rate=100, random_state=42)
    DATA_tsne = tsne.fit_transform( POINTS_array )

    plt.figure(figsize=(10, 8))

    # cmap = plt.cm.rainbow
    # color = cmap(np.linspace(0, 1, len(spec) ))

    color = [
        '#E61919',  # red
        '#1919E6',  # blue
        '#177317',  # green
        '#E6E619',  # yellow
        '#731973',  # purple
        '#E6B2BC',  # pink
        '#953A3A',  # brown
        '#E6A019',  # orange
        '#000000',  # black
        '#19E6E6',  # cyan
        '#79C3E6',  # skyblue
        '#E619E6',  # magenta
        '#19E619',  # lime
        '#E6C719',  # gold
        '#177373',  # teal
        '#171773',  # navy
        '#737373',  # grey
        '#731717',  # maroon
        '#737317'   # olive
    ]

    # zmapowanie etykiet na kolory
    colors_laybel: Dict[str, any] = {
        k: color[i]
        for i, k in enumerate(class_label_counter.keys())
    }

    PLOT_LB = None

    # rysowanie punktu każdej chmury
    for index, lb in enumerate(LABEL_array):

        xi = DATA_tsne[index, 0]
        yi = DATA_tsne[index, 1]

        # dodanie po jednej etykiecie do legendy
        if lb != PLOT_LB :
            plt.scatter(
                        xi, yi,
                        color=colors_laybel[lb],
                        marker='x',
                        s=30,
                        label=lb
            )
            PLOT_LB = lb
        else:
            plt.scatter(
                xi, yi,
                color=colors_laybel[lb],
                marker='x',
                s=30,
            )

    plt.title(f"T-SNE visualization in perplexity {perplexity}")
    plt.xlabel("T-SNE dim 1")
    plt.ylabel("T-SNE dim 2")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    plt.tight_layout()
    plt.grid(True)

    save_path = os.path.join( PATH.axes_nonspec, f"T-SNE-{perplexity}.jpg")
    plt.savefig(save_path, format="jpg", dpi=300)
    LOG.print(f"=[SAVE] Save T-SNE plot to: {save_path}")

    LOG.print(f"\n[ENDPROC] End drawing T-SNE")


if __name__ == '__main__' and 1:

    from src.func.special import JSON, NPY

    L = NPY.load(  "modif_"+NPY.LABEL )
    P = NPY.load(  "modif_"+NPY.POINTS)
    clc = JSON.load( "modif_"+JSON.class_label_counter )

    # distribution_of_class_label_points(L, P, clc)
    T_SNE(L, P, clc, perplexity=50)
