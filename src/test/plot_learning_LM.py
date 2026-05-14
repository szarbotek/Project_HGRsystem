"""
    Program pozwala na rysowanie wykresu porcesu uczenia LM

"""


from data.project_values import *

from src.func.special import NPY, MODEL_H5, JSON, CSV

from matplotlib import pyplot as plt

df_history = CSV.load("history")


from sklearn.metrics import classification_report, confusion_matrix

LOG.print(f"[PLOT] Draw plot ")

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(df_history['val_accuracy'], label='Val Accuracy', color='orange')
plt.plot(df_history['accuracy'], label='Train Accuracy', color='green')

plt.title('Precision (Accuracy)')
plt.xlabel('Epochs')
plt.ylabel('Percent [%]')
plt.grid(True, alpha=0.5)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(df_history['val_loss'], label='Val Loss', color='orange')
plt.plot(df_history['loss'], label='Train Loss', color='green')

plt.title('Precision (Loss)')
plt.xlabel('Epochs')
plt.ylabel('Loss function')
plt.legend()
plt.grid(True, alpha=0.5)


plt.savefig(os.path.join(PATH.axes_train , "precision.jpg" ), dpi=300)
LOG.print(f"=[SAVE] Saving plot")
