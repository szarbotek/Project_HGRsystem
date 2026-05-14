import cv2
from numpy.typing import NDArray

def draw_landmark( image: NDArray, landmark  ) -> NDArray:

    # pobranie wymiarów zdjecia
    higth, wigth, _ = image.shape

    # mapa połaczeń
    points_composytion_pattern = [
        (0,1), (1,2), (2,3), (3,4),
        (0,5), (5,6), (6,7), (7,8),
        (0,9), (9,10), (10,11), (11,12),
        (0,13), (13,14), (14,15), (15,16),
        (0,17), (17,18), (18,19), (19,20)
    ]

    # pozycjonowanie punktów na obrazie, odczytanych z ladnamku


    points = [ (  int(pos.x*wigth), int(pos.y*higth) ) for pos in landmark  ]

    # rysowanie połaczeń miedzy punktami
    for pcp in points_composytion_pattern:
        cv2.line( image, points[pcp[0]],  points[pcp[1]],  color=(0,255,0), thickness=2)

    # rysowanie punktów
    for p in points:
        cv2.circle( image, p, 3, (0,0, 255), -1)

    # for landmark in hand_landmarks:
    #     points = [ (  int(pos.x*wigth), int(pos.y*higth) ) for pos in landmark  ]
    #
    #     # rysowanie połaczeń miedzy punktami
    #     for pcp in points_composytion_pattern:
    #         cv2.line( image, points[pcp[0]],  points[pcp[1]],  color=(0,0,255), thickness=2)
    #
    #     # rysowanie punktów
    #     for p in points:
    #         cv2.circle( image, p, 2, (255,255, 0), -1)

    return image