# AgriCare/server/utils/geogrid.py

from h3 import latlng_to_cell, grid_disk

H3_RESOLUTION = 8
RADIUS_K_MAP = {1:1, 2:2, 3:4, 4:5, 5:6, 6:7, 7:8, 8:10, 9:11, 10:12}


def get_h3_index(latitude: float, longitude: float):
    return latlng_to_cell(latitude, longitude, H3_RESOLUTION)

def get_k_ring(latitude: float, longitude: float, radius: int):
    origin = get_h3_index(latitude, longitude)
    return grid_disk(origin, RADIUS_K_MAP.get(radius))
