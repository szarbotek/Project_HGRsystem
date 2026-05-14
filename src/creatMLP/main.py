
from creatMLP.connetion import generate_path_connection_to_sampes
from creatMLP.recognition import  generate_array_of_class_data, add_gesture_thumb_index_inv
from creatMLP.layerFPR import acctivate_FPR

from  plot import visual2d
from creatMLP.train import activate_train

def readTime():
    from func.special import NPY, JSON

    Larr = NPY.load(NPY.LABEL)
    Parr = NPY.load(NPY.POINTS)
    clc = JSON.load(JSON.class_label_counter)

    return Larr, Parr, clc


limit_per_class = 2000

#pobranie ścierzek
class_label_set, clc = generate_path_connection_to_sampes( limit_per_class=limit_per_class  )

visual2d.distribution(clc, FLAG_save=True, name="connection" )

#generacja tablic danych z normalizacją
Larr, Parr, clc = generate_array_of_class_data(class_label_set, limit_per_class=limit_per_class)

# Larr, Parr, clc = readTime()

visual2d.distribution(clc, FLAG_save=True, name="recognition" )
visual2d.distribution_of_class_label_points(Larr, Parr, clc, target_folder="non_threshold")

# filtracja FPR
Larr, Parr, clc = acctivate_FPR(Larr, Parr, clc, threshold=0.15, )

visual2d.distribution(clc, FLAG_save=True, name="threshold" )
visual2d.distribution_of_class_label_points(Larr, Parr, clc, target_folder="threshold")

# aktywowanie modelu
activate_train(Larr, Parr, clc)

