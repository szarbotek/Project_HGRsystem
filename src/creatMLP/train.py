"""
    Program odpowiada za trenowanie modelu na przygotowanych danych

"""
import os.path

from data.project_values import *

import random

import numpy as np
from numpy.typing import NDArray
from typing import Dict, Union, Sequence, Tuple

from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from src.func.special import NPY, MODEL_H5, JSON, CSV
from src.func.analyzing_tool import data_separate

def activate_train(
            LABEL_array: NDArray, POINTS_array: NDArray,
            class_label_counter: Dict[str, int],  name: str = "point_recognition"
        ) -> Tuple[NDArray[np.float64], NDArray[np.float64],NDArray[np.float64], NDArray[np.float64],NDArray[np.float64], NDArray[np.float64]]:
    """
        Funkcja odpowiada za przygotowanie konfiguracji modelu oraz uruchomienie trenowania

    """

    LOG.print(f"\n[PROC] Model tf training process")

    encoder = LabelEncoder()

    # zmapowanie etykiet na wartości numneryczne
    LABEL_transform = encoder.fit_transform(LABEL_array)

    # przyogotanie unikalnych wektorów one-hot dla każdej klasy
    LABEL_onehot_array = tf.keras.utils.to_categorical(LABEL_transform)

    NPY.save( NPY.classes, encoder.classes_ )

    LOG.print(f".[INFO] base data: {LABEL_array.shape}, {POINTS_array.shape}) ")

    # podział danych
    LOG.print(f".[INFO] Split data")
    train_labels, train_points, test_labels, test_points, valid_labels, valid_points = data_separate( LABEL_onehot_array, POINTS_array, class_label_counter )

    LOG.print(f".[INFO] train data: {train_labels.shape} {train_points.shape}")
    LOG.print(f".[INFO] test data:  {test_labels.shape}  {test_points.shape}")
    LOG.print(f".[INFO] valid data: {valid_labels.shape} {valid_points.shape}")

    # konfiguracja warst
    model = Sequential([
        # 63 Tokens
        Dense(128, activation='relu', input_shape=(63,)),
        BatchNormalization(),
        Dropout(0.4),

        # Layer 1
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),

        # Layer 2
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),

        # Out layer
        Dense(len(encoder.classes_), activation='softmax')
    ])

    # konfiguracja optymalizatora
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # przerwanie uczenie w przypadku spadku błedu walidacyjnego i powrót do sytuacji kiedy bład był najniższy
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-5, verbose=1)
    ]

    # wprowadzenie danych do modelu
    run = model.fit(
        train_points, train_labels,
        validation_data=(valid_points, valid_labels),
        epochs=100,
        batch_size=64,
        callbacks=callbacks,
        verbose=1
    )


    MODEL_H5.save( MODEL_H5.base_name, model )

    CSV.save( "history", run.history )
    CSV.save("labels", LABEL_onehot_array)
    CSV.save("points", POINTS_array)

    NPY.save( "history", run.history )

    NPY.save("train_points", train_points)
    NPY.save("train_labels", train_labels)

    NPY.save("valid_points", valid_points)
    NPY.save("valid_labels", valid_labels)

    NPY.save("test_points", test_points)
    NPY.save("test_labels", test_labels)

    LOG.print(f"[ENDPROC] End of training")

    return train_labels, train_points, test_labels, test_points, valid_labels, valid_points


if __name__ == '__main__':

    from func.special import NPY, JSON

    L = NPY.load("FPR_" +NPY.LABEL)
    P = NPY.load("FPR_" +NPY.POINTS)
    clc = JSON.load("FPR_" + JSON.class_label_counter)

    activate_train(L, P, clc )


