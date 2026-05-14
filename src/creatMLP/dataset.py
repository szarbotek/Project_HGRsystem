"""
    Baza zdjęć została zapisana w określonej ścieżce na dysku. Zawiera około 1 086 158 zdjęć, co odpowiada około 120 GB
    danych w rozdzielczości 512p.

    Program ma za zadanie skopiować dane oraz przenieść je do katalogówz odpowiednim etykietowaniem klasowym.
"""

# from pathlib import Path
# import sys
#
# ROOT = Path(__file__).resolve().parent.parent
# sys.path.append(str(ROOT))

from data.project_values import *

import random
import shutil

"""
    przetransportowanie i wprowadzenie odpowiedniego zbioriu około 2 tys. zdjeć 
"""

def creat_project_labels_folder()->None:
    """
        Funckja tworzy strukture folderów odpowiadającym eykietom klas modelu LM
    :return:
    """
    LOG.print("[PROC] Creat folder structure")
    fd_target =  "model_training"

    fd = os.path.join(PATH.image, fd_target)

    if not os.path.exists( fd ):
        LOG.print( f".[INFO] Folder: {fd_target} non-exists, in path: {PATH.image}")
        os.mkdir( fd )
        LOG.print(f".[INFO] Creat: {fd_target}, in path: {PATH.image}")

    for lb in DATASET_labels:
        lb_path = os.path.join(fd, lb)
        if os.path.exists(lb_path):
            LOG.print(f".[INFO] Folder already exists, in path: {lb_path}")
        else:
            os.mkdir(lb_path)
            LOG.print(f".[INFO] Make dir {lb_path}")

    LOG.print(f"[ENDPROC] Folder structure successfully created")
    return

def copy_dataset(sample_per_label: int = 10, file_format:str = "jpg", full_dataset_path: str = PATH.full_dataset)->None:
    """
        Funkcja kopuje n' próbek z zbioru docelowego. Przy czym kopiowanie uwzglednia zgodność nazewnictwa etykiet jako
        folderów

    :param sample_per_label:
    :param file_format:
    :param full_dataset_path: pobierane z project_values.py
    :return:
    """
    creat_project_labels_folder()

    LOG.print( "[PROC] Select and coppy samples for LM model to inside dataset" )

    fd_target = "model_training"

    # przejscie po etykietach klas
    for index, lb in enumerate(DATASET_labels):

        bff00 = len(DATASET_labels)
        LOG.print( f".[INFO] { LOG.counter(index, bff00) } Copy label: {lb}")

        target_path = os.path.join( PATH.image, fd_target, lb )
        setload_path = os.path.join( full_dataset_path, lb )

        try:
            assert os.path.exists( target_path ), FileExistsError(target_path)
            assert os.path.exists( setload_path ), FileExistsError(setload_path)

            data_full = os.listdir(setload_path)
            data_size = len(data_full)

            assert data_size >= sample_per_label, IndexError

            # wybranie unikatowych próbek
            data_sample = random.sample(data_full, sample_per_label)

            for iname, ds in enumerate(data_sample):

                #LOG.print(f"..[INFO] {LOG.counter(iname, sample_per_label)} sampling")

                target_name = f"{iname}.{file_format}"

                # kopiowanie do folderu docelowego
                ph2load = os.path.join(setload_path, ds)
                ph2copy = os.path.join(target_path, target_name)
                shutil.copy2( ph2load, ph2copy)

        except (FileExistsError, AssertionError) as e:
            LOG.print(f"<ERR> Target folder exists, in path: {e}")
        except IndexError:
            LOG.print(f"<ERR> Not enough data to copy from dataset label: {lb}")
        except PermissionError as e:
            LOG.print(f"<ERR> Access Denied: {e}")

    LOG.print(f"[ENDPROC] Dataset successfully created")
    return

if __name__ == "__main__":

    copy_dataset( sample_per_label=1 )

r"""
    [INFO] ROOT complete P:\INZ\ProjectPD
    [PROC] Creat folder structure
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\fist
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\stop
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\one
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\peace
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\three
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\little_finger
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\call
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\rock
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\three3
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\grip
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\like
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\thumb_index
    .[INFO] Folder already exists, in path: P:\INZ\ProjectPD\assets\image\model_training\dislike
    [ENDPROC] Folder structure successfully created
    [PROC] Select and coppy samples for LM model to inside dataset
    .[INFO] ( 0:13) Copy label: fist
    .[INFO] ( 1:13) Copy label: stop
    .[INFO] ( 2:13) Copy label: one
    .[INFO] ( 3:13) Copy label: peace
    .[INFO] ( 4:13) Copy label: three
    .[INFO] ( 5:13) Copy label: little_finger
    .[INFO] ( 6:13) Copy label: call
    .[INFO] ( 7:13) Copy label: rock
    .[INFO] ( 8:13) Copy label: three3
    .[INFO] ( 9:13) Copy label: grip
    .[INFO] (10:13) Copy label: like
    .[INFO] (11:13) Copy label: thumb_index
    .[INFO] (12:13) Copy label: dislike
    [ENDPROC] Dataset successfully created
"""