
"""
    otwarcie ścierzki
    sample 2000 sztuk

"""

PATH = r"D:\INZ_PHOTO_DATA\assets\hagridv2_512_open\HaGRIDv2_dataset_512"


# [ print( f"[{i}/{len(os.listdir(PATH))}]", f, len(os.listdir(os.path.join(PATH, f) )) ) for i, f in enumerate(os.listdir(PATH)) ]

import random

# Twoja lista 30 000 elementów
lista = list(range(30000))

# Wybór 2 000 unikalnych elementów
losowe_elementy = random.sample(lista, 2000)