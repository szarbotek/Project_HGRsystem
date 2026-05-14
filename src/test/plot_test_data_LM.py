"""
    Program pozwala na rysowanie wykresu danych testowych

"""

from data.project_values import *

from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

from src.func.special import NPY, MODEL_H5, JSON, CSV
from matplotlib import pyplot as plt
import seaborn as sns

test_labels = NPY.load( "test_labels")
test_points = NPY.load( "test_points")

classes = NPY.load( "classes")

model = MODEL_H5.load( MODEL_H5.base_name )

LOG.print(f"[PLOT] Draw plot ")

label_pred = np.argmax(model.predict(test_points), axis=1)
label_true = np.argmax(test_labels, axis=1)

plt.figure(figsize=(20, 15))

cm = confusion_matrix(label_true, label_pred)

sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)

plt.title("Confusion Matrix", fontsize=20)
plt.xlabel("Predict", fontsize=15)
plt.ylabel("Real" , fontsize=15)

plt.xticks( rotation=90, fontsize=12)
plt.yticks( rotation=0, fontsize=12)

plt.savefig(os.path.join(PATH.axes_train , "confiusion_matrix.jpg" ), dpi=300)
LOG.print(f"=[SAVE] Saving plot")

LOG.print(f".[INFO] CLASSIFICATION REPORT ")
LOG.print( classification_report(label_true, label_pred, target_names=classes) )
