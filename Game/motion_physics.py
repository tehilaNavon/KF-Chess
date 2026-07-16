from constants import METERS_PER_CELL, MS_PER_SECOND


def compute_chebyshev_distance(source, destination):
    row_distance = abs(destination.row - source.row)
    col_distance = abs(destination.col - source.col)
    return max(row_distance, col_distance)


def compute_travel_duration_ms(distance_cells, speed_m_per_sec, meters_per_cell=METERS_PER_CELL):
    if distance_cells == 0 or speed_m_per_sec <= 0:
        return 0
    distance_meters = distance_cells * meters_per_cell
    return int((distance_meters / speed_m_per_sec) * MS_PER_SECOND)


def compute_animation_duration_ms(frame_count, frames_per_sec):
    if frame_count <= 0 or frames_per_sec <= 0:
        return 0
    return int((frame_count / frames_per_sec) * MS_PER_SECOND)
