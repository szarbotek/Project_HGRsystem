"""
    Program odpowiada za przygotowanie dostępu do zbioru zdjęć do analizy, na podstawie wybranych zdjęć zgromadzonych
    w projekcie.
"""

from data.project_values import *
from src.func.special import JSON
from src.plot.visual2d import distribution

import random

from typing import Dict, Sequence, Tuple

def generate_path_connection_to_sampes(limit_per_class: int = LIMIT_PER_CLASS)->Tuple[ Dict[str, Sequence[str]], Dict[str, int] ]:
    """
        Funkcja generuje słownik etykier klas i zapisuje w nim ścierzki docelowe próbek

        :param limit_per_class: Ilosc pobieranych próbek na klase
        :return: Zwracana zostaje wskazana struktura path2sample dla etykiet klas
    """

    LOG.print( "\n[PROC] Preparetion of dataset path structure" )
    fd_dataset = "model_training"

    # utorzenie ścierzki do zbioru danych
    dataset = os.path.join( PATH.image, fd_dataset)

    if os.path.exists( dataset ):
        LOG.print( ".[INFO] Find dataset")
    else:
        raise FileNotFoundError( f"<ERR> Dataset non-exists {dataset}")

    class_lb_path = os.listdir( dataset )
    LOG.print(f".[INFO] Find class label: {class_lb_path}, {len(class_lb_path)}")

    class_label_set: Dict[str, Sequence[str]] = {}
    counter: Dict[str, int] = {}

    # dodanie scierzek docelowych do zbioru zdjec etykiety klasy
    for lb in class_lb_path:

        fd_samples = os.path.join( dataset , lb )
        try:
            assert os.path.exists( fd_samples ), FileNotFoundError

            img_full_path = [
                os.path.join( fd_samples, img )
                for img in os.listdir( fd_samples )
            ]

            class_label_set[lb] = random.sample( img_full_path, limit_per_class )
            counter[lb] = len( class_label_set[lb]  )

            LOG.print(f".[INFO] Add { counter[lb] } samples to {lb}")

        except (FileNotFoundError, AssertionError):
            LOG.print(f"<ERR> No image data dor Class label {lb}")
            continue

    distribution( counter, FLAG_save=True, name="Distribution_before_NFPR", target_folder="distbt", title="distribution before NFPR" )

    # zapisanie jsona
    JSON.save( JSON.class_label_counter, counter)

    LOG.print(f"[ENDPROC] Succes, connetion created")
    return class_label_set, counter

if __name__ == '__main__' and 0:
    generate_path_connection_to_sampes(1, )