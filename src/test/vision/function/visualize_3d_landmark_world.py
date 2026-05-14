from types import NoneType
from typing import List

import open3d as o3d
import numpy as np
import  random
import math


def draw_3d_landmarks_by_points( points: List[float] ):


    all_objects = []

    normalized_points = np.array( list(points), dtype=np.float64).reshape(-1, 3)

    color = [random.random(), random.random(), random.random()]

    # Punktowa chmura
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(normalized_points)

    # Ustawienie koloru punktów na czerwony
    # Tworzymy tablicę o tym samym rozmiarze co punkty, wypełnioną [1, 0, 0]
    num_points = len(normalized_points)
    pcd.colors = o3d.utility.Vector3dVector(np.tile(color, (num_points, 1)))

    # Krawędzie MediaPipe Hands
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (0, 9), (9, 10), (10, 11), (11, 12),
        (0, 13), (13, 14), (14, 15), (15, 16),
        (0, 17), (17, 18), (18, 19), (19, 20),
        (5, 9), (9, 13), (13, 17),
    ]

    lines = o3d.geometry.LineSet()
    lines.points = pcd.points
    lines.lines = o3d.utility.Vector2iVector(connections)

    # Ustawienie koloru linii na czerwony
    # Tworzymy tablicę o rozmiarze odpowiadającym liczbie połączeń
    num_lines = len(connections)
    lines.colors = o3d.utility.Vector3dVector(np.tile(color, (num_lines, 1)))

    all_objects.extend([pcd, lines])

    return all_objects


def draw_hand_landmarks( hand_landmarks ):
    all_objects = []

    for landmark in hand_landmarks:
        if isinstance(landmark, NoneType): continue

        points = np.array( np.array([lm.x, lm.y, lm.z]) for lm in landmark )

        normalized_points = points

        color = [random.random(), random.random(), random.random()]

        # Punktowa chmura
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(normalized_points)

        # Ustawienie koloru punktów na czerwony
        # Tworzymy tablicę o tym samym rozmiarze co punkty, wypełnioną [1, 0, 0]
        num_points = len(normalized_points)
        pcd.colors = o3d.utility.Vector3dVector(np.tile(color, (num_points, 1)))

        # Krawędzie MediaPipe Hands
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17),
        ]

        lines = o3d.geometry.LineSet()
        lines.points = pcd.points
        lines.lines = o3d.utility.Vector2iVector(connections)

        # Ustawienie koloru linii na czerwony
        # Tworzymy tablicę o rozmiarze odpowiadającym liczbie połączeń
        num_lines = len(connections)
        lines.colors = o3d.utility.Vector3dVector(np.tile(color, (num_lines, 1)))

        all_objects.extend([pcd, lines])
    return all_objects


def visualize_hand_landmark( hand_landmarks ):

    all_objects = draw_hand_landmarks( hand_landmarks )

    o3d.visualization.draw_geometries( all_objects )


def get_axies(size=1):
    points = np.array([
        [0, 0, 0],
        [size, 0, 0],
        [0, size, 0],
        [0, 0, size]
    ])

    lines = [[0, 1], [0, 2], [0, 3]]
    colors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    line_set.lines = o3d.utility.Vector2iVector(lines)
    line_set.colors = o3d.utility.Vector3dVector(colors)

    return line_set