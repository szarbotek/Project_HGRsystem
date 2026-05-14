import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT))

from data.project_values import *

import json
import numpy as np
from numpy.typing import NDArray
from typing import Dict

import pandas as pd

import tensorflow as tf

class JSON:

    # licznik wystąpień próbek na etykiete klasy
    class_label_counter: str = "class_label_counter"

    @staticmethod
    def save(name:str, data: Dict[any, any])->None:
        """
            Funkcja zapisuje JSON w data/JSON
        """
        try:
            fname = PATH.get_file(name, "json")

            save_path = os.path.join(
                PATH.data_JSON,
                fname
            )

            with open(save_path, 'w') as f:
                json.dump(data, f)
            LOG.print(f"=[SAVE] Save as: {fname} to {PATH.data_JSON}")
        except Exception as e:
            LOG.print(f"<ERR> JSON cannot be save, {e}")

    @staticmethod
    def load(name:str)->Dict | None:
        """
            Funkcja wczytuje JSON z data/JSON
        """
        try:
            load_path = os.path.join(
                PATH.data_JSON,
                PATH.get_file(name, "json")
            )

            ret: Dict | None = None

            with open(load_path, 'r') as f:
                ret = json.load(f)

            LOG.print(f".[INFO] Load json {load_path}")

            return ret
        except Exception as e:
            LOG.print(f"<ERR> JSON cannot be load, {e}")
            return None


class NPY:

    LABEL = "LABEL_array"
    POINTS = "POINTS_array"
    classes = "classes"

    @staticmethod
    def save(name: str, data: NDArray) -> None:
        """
            Funkcja zapisuje NPY w data/numerical
        """
        try:
            fname = PATH.get_file(name, "npy")

            save_path = os.path.join(
                PATH.data_numerical,
                fname
            )

            np.save(save_path, data)

            LOG.print(f"=[SAVE] Save as: {fname} to {PATH.data_numerical}")
        except:
            LOG.print(f"<ERR> NPY cannot be save")

    @staticmethod
    def load(name: str, allow_pickle=False) -> NDArray | None:
        """
            Funkcja wczytuje NPY z data/numerical
        """
        try:
            load_path = os.path.join(
                PATH.data_numerical,
                PATH.get_file(name, "npy")
            )

            ret: NDArray | None = None

            ret = np.load(load_path,  allow_pickle=allow_pickle)

            LOG.print(f".[INFO] Load json {load_path}")

            return ret
        except:
            LOG.print(f"<ERR> NPY cannot be load")
            return None


class MODEL_H5:

    base_name = "classifier"

    @staticmethod
    def save(name: str, model: tf.keras.Model) -> None:
        """
            Funkcja zapisuje model h5 w models
        """
        try:
            fname = PATH.get_file(name, "h5")

            save_path = os.path.join(
                PATH.models,
                fname
            )

            tf.keras.models.save_model(model=model, filepath=save_path)

            LOG.print(f"=[SAVE] Save as: {fname} to {PATH.models}")
        except:
            LOG.print(f"<ERR> h5 model cannot be save")

    @staticmethod
    def load(name: str) -> tf.keras.Model | None:
        """
            Funkcja wczytuje model h5 z models
        """
        try:
            load_path = os.path.join(
                PATH.models,
                PATH.get_file(name, "h5")
            )

            ret: tf.keras.Model | None = None

            ret = tf.keras.models.load_model(load_path)

            LOG.print(f".[INFO] Load  h5 model {load_path}")

            return ret
        except:
            LOG.print(f"<ERR> h5 model cannot be load")
            return None


class CSV:

    @staticmethod
    def save(name: str, data: any) -> None:
        """
            Funkcja zapisuje CSV w data/csv
        """
        try:
            df = pd.DataFrame(data)

            fname = PATH.get_file(name, "csv")

            save_path = os.path.join(
                PATH.data_csv,
                fname
            )

            pd.DataFrame.to_csv( df, save_path, encoding="utf-8" )

            LOG.print(f"=[SAVE] Save as: {fname} to {PATH.data_csv}")
        except Exception as e:
            LOG.print(f"<ERR> CSV cannot be save, {e}")

    @staticmethod
    def load(name: str) -> pd.DataFrame | None:
        """
            Funkcja wczytuje CSV z data/csv
        """
        try:
            load_path = os.path.join(
                PATH.data_csv,
                PATH.get_file(name, "csv")
            )

            ret: pd.DataFrame | None = None

            ret = pd.read_csv(load_path)

            LOG.print(f".[INFO] Load CSV {load_path}")

            return ret
        except Exception as e:
            LOG.print(f"<ERR> CSV cannot be load, {e}")
            return None
