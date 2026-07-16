from constants import MS_PER_SECOND


def cell_top_left_pixel(row, col, cell_size):
    pixel_x = col * cell_size
    pixel_y = row * cell_size
    return pixel_x, pixel_y


def centered_draw_position(cell_x, cell_y, cell_size, sprite_width, sprite_height):
    draw_x = cell_x + (cell_size - sprite_width) // 2
    draw_y = cell_y + (cell_size - sprite_height) // 2
    return draw_x, draw_y


def interpolate_value(start_value, end_value, progress):
    clamped_progress = max(0.0, min(1.0, progress))
    return start_value + (end_value - start_value) * clamped_progress


def compute_frame_index(elapsed_ms, frames_per_sec, frame_count, is_loop):
    if frame_count <= 0 or frames_per_sec <= 0:
        return 0
    frame_duration_ms = MS_PER_SECOND / frames_per_sec
    raw_index = int(elapsed_ms / frame_duration_ms)
    if is_loop:
        return raw_index % frame_count
    return min(raw_index, frame_count - 1)
