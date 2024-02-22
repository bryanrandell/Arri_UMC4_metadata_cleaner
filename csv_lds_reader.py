import csv
import os
import time

# todo not very memory and cpu efficient
# path = "METADATA/A270_META"


def get_multiple_csv_data(path: str) -> tuple:
    list_csv_files_path = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    headers_list = []
    rows_list = []
    for csv_file_path in list_csv_files_path:
        with open(csv_file_path) as csv_file:
            csv_file_read = csv.reader(csv_file, delimiter='\t')
            header = next(csv_file_read)
            rows = [row for row in csv_file_read]
            headers_list.append(header)
            rows_list.append(rows)
    return list_csv_files_path, headers_list, rows_list


def convert_csv_to_list(csv_file_path: str) -> tuple:
    with open(csv_file_path) as csv_file:
        csv_file_read = csv.reader(csv_file, delimiter='\t')
        header = next(csv_file_read)
        rows = [row for row in csv_file_read]
    return header, rows


def extract_tc_from_string(tc_string: str) -> tuple:
    hours = int(tc_string.split(":")[0])
    minutes = int(tc_string.split(':')[1])
    seconds = int(tc_string.split(':')[2])
    frames = int(tc_string.split(':')[3])
    return hours, minutes, seconds, frames


# todo very slow if offset is large
# def apply_offset_in_frames(tuple_int_tc: tuple, offset_in_frames: int, project_fps: int = 24) -> tuple:
#     start_time_function = time.time()
#     hours, minutes, seconds, frames = tuple_int_tc
#     if offset_in_frames > 0:
#         for i in range(offset_in_frames):
#             if frames == project_fps:
#                 seconds += 1
#                 frames = 0
#             if seconds == 60:
#                 minutes += 1
#                 seconds = 0
#             # print(i, minutes, sep=" mins-- ")
#             if minutes == 60:
#                 hours += 1
#                 minutes = 0
#             # print(i, hours, sep=" hours-- ")
#             # print("{} - {} - {} - {}".format(hours, minutes, seconds, frames), end='\r')
#             frames += 1
#             print(f"{time.time() - start_time_function:.2f} seconds", end="\r")
#     else:
#         for i in range(abs(offset_in_frames)):
#             if frames == 0:
#                 seconds -= 1
#                 frames = project_fps
#             if seconds == 0:
#                 minutes -= 1
#                 seconds = 60
#             if minutes == 0:
#                 hours -= 1
#                 minutes = 60
#             # print(i, minutes, sep=" mins-- ")
#             # print("{} - {} - {} - {}".format(hours, minutes, seconds, frames), end='\r')
#             frames -= 1
#
#     return hours, minutes, seconds, frames
#
#
# def reconstruct_tc_from_tuple_int(tuple_int_tc: tuple) -> str:
#     return '{:02d}:{:02d}:{:02d}:{:02d}'.format(tuple_int_tc[0],
#                                                 tuple_int_tc[1],
#                                                 tuple_int_tc[2],
#                                                 tuple_int_tc[3])


def tc_offsetter(rows: list, offset_in_frames: int) -> list:
    rows_list_with_offset = []
    tc_column = (tc[1] for tc in rows)
    # apply offset
    tuple_from_tc_list = (extract_tc_from_string(tc) for tc in tc_column)
    apply_offset = (apply_offset_in_frames(tuple_from_tc, offset_in_frames) for tuple_from_tc in tuple_from_tc_list)
    # reconstruct tc
    tc_column = (reconstruct_tc_from_tuple_int(tc) for tc in apply_offset)
    # replace tc in rows
    for i, tc in enumerate(tc_column):
        rows[i][1] = tc
        rows_list_with_offset.append(rows[i])
    return rows_list_with_offset


def timecode_operation(base_tc: str, new_start_tc: str, project_fps: int = 24) -> int:
    base_hours, base_minutes, base_seconds, base_frames = extract_tc_from_string(base_tc)
    new_hours, new_minutes, new_seconds, new_frames = extract_tc_from_string(new_start_tc)
    offset_in_frames = (new_hours - base_hours) * 60 * 60 * project_fps + (new_minutes - base_minutes) * 60 * project_fps + (new_seconds - base_seconds) * project_fps + (new_frames - base_frames)
    print(offset_in_frames)
    return offset_in_frames

def offset_to_tuple(tuple_int_tc: tuple, offset_in_frames: int) -> tuple:
    offset_in_hours = offset_in_frames // (60 * 60 * 24)
    offset_in_minutes = offset_in_frames // (60 * 24) % 60
    offset_in_seconds = offset_in_frames // 24 % 60
    offset_in_frames = offset_in_frames % 24
    new_hours = tuple_int_tc[0] + offset_in_hours
    new_minutes = tuple_int_tc[1] + offset_in_minutes
    new_seconds = tuple_int_tc[2] + offset_in_seconds
    new_frames = tuple_int_tc[3] + offset_in_frames
    return new_hours, new_minutes, new_seconds, new_frames


# def apply_offset(tc_column: list, offset_in_frames: int) -> list:
#     # apply offset
#     tuple_from_tc_list = (extract_tc_from_string(tc) for tc in tc_column)
#     apply_offset = (apply_offset_in_frames(tuple_from_tc, offset_in_frames) for tuple_from_tc in tuple_from_tc_list)
#     # reconstruct tc
#     tc_column = (reconstruct_tc_from_tuple_int(tc) for tc in apply_offset)
#     # replace tc in rows
#     for i, tc in enumerate(tc_column):
#         rows[i][1] = tc
#         rows_list_with_offset.append(rows[i])
#     return rows_list_with_offset


def change_start_tc(rows: list, new_start_tc: str, fps: int = 24) -> list:
    rows_list_with_offset = []
    tc_column = (tc[1] for tc in rows)
    start_tc = rows[0][1]
    offset_in_frames = calculate_new_start_tc_offset(start_tc, new_start_tc)
    # apply offset
    # tuple_from_tc_list = (convert_tc_to_frames(tc) for tc in tc_column)
    # calculate offset
    apply_offset = (operation_tc(tc, offset_in_frames, fps) for tc in tc_column)
    # reconstruct tc
    # tc_column = (convert_frames_to_tc(tc_frames) for tc_frames in apply_offset)
    # replace tc in rows
    for i, tc in enumerate(apply_offset):
        rows[i][1] = tc
        rows_list_with_offset.append(rows[i])
    return rows_list_with_offset


def create_copy_csv_file(csv_file_path: str, headers_list: list, rows_list: list) -> None:
    with open(f"{csv_file_path.split('.')[0]}_tc_offset_copy.csv", 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        writer.writerow(headers_list)
        print('starting writing rows')
        writer.writerows(rows_list)


def operation_tc(tc: str, offset: int, fps: int) -> str:
    new_tc = convert_tc_to_frames(tc) + offset
    return convert_frames_to_tc(new_tc, fps)


def calculate_new_start_tc_offset(start_tc: str, new_start_tc: str) -> int:
    return convert_tc_to_frames(new_start_tc) - convert_tc_to_frames(start_tc)


def convert_tc_to_frames(tc, fps = 24):
    in_frames = int(tc.split(":")[0]) * 60 * 60 * fps + int(tc.split(":")[1]) * 60 * fps + int(
        tc.split(":")[2]) * fps + int(tc.split(":")[3])
    return in_frames


def convert_frames_to_tc(frames_num, fps = 24):
    hours = frames_num // (3600 * fps)
    minutes = (frames_num // (60 * fps)) % 60
    seconds = (frames_num // fps) % 60
    frames = frames_num % (fps)
    return "{:02d}:{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds, frames)


def erase_rows(rows: list, erase_top_num: int = 0, erase_bottom_num: int = 0) -> list:
    return rows[erase_top_num:len(rows) - erase_bottom_num]


def extract_total_frames(rows: list) -> int:
    return len(rows)


def extract_camera_index(rows: list, header: list) -> str:
    camera_index = rows[-1][header.index('Camera Index')]
    return camera_index


def extract_start_tc(rows: list, header: list) -> str:
    start_tc = rows[0][header.index('Master TC')]
    return start_tc


def extract_end_tc(rows: list, header: list) -> str:
    end_tc = rows[-1][header.index('Master TC')]
    return end_tc


def crop_csv_file_with_tc(csv_file_path: str, new_csv_file_path: str, video_start_tc: int) -> str:
    headers_list, rows = convert_csv_to_list(csv_file_path)
    column_index = headers_list.index('Index')
    column_tc = headers_list.index('Master TC')
    rows_list = []
    index = 0
    for row in rows:
        row_tc_frame = convert_tc_to_frames(row[column_tc])
        if row_tc_frame >= video_start_tc:
            row[column_index] = str(index)
            rows_list.append(row)
            index += 1
    # recreate index column
    create_copy_csv_file(new_csv_file_path, headers_list, rows_list)
    return new_csv_file_path


def add_dummy_rows_to_csv_end(rows: list, header: list, meta_frame_set: set, video_frame_set: set, add_filler: bool = False, dummy_filler: str = "") -> list:
    difference_intersection_sets = meta_frame_set.difference(video_frame_set)
    new_rows = rows
    end_csv_tc = convert_tc_to_frames(rows[-1][header.index('Master TC')])
    end_index = int(rows[-1][header.index('Index')])
    for i in range(difference_intersection_sets):
        dummy_row = ["" for i in range(len(header))]
        dummy_row[header.index('Index')] = str(end_index + i)
        dummy_row[header.index('Master TC')] = convert_frames_to_tc(end_csv_tc + i)
        new_rows.append(dummy_row)
    return new_rows


def merge_cam_metadata_to_csv_column(rows: list, header: list, cam_meta: dict, add_meta_to_all_rows: bool = False) -> tuple:
    rows_merged = []
    header_merged = header + [index for index in cam_meta.keys()]
    # index_new_element = len(header)
    for index, row in enumerate(rows):
        if add_meta_to_all_rows:
            new_row = row + [value for value in cam_meta.values()]
            rows_merged.append(new_row)
        else:
            if index == 0:
                new_row = row + [value for value in cam_meta.values()]
                rows_merged.append(new_row)
            else:
                rows_merged.append(row)
    return rows_merged, header_merged


def main(csv_file_path: str, offset_in_frames: int, new_start_tc: str, change_tc_by_offset: bool = True) -> None:
    start_time = time.time()
    headers_list, rows_list = convert_csv_to_list(csv_file_path)
    if change_tc_by_offset:
        rows_list_with_offset = tc_offsetter(rows_list, offset_in_frames)
    else:
        rows_list_with_offset = change_start_tc(rows_list, new_start_tc)
    print(f"creating csv file... started at {time.time() - start_time} seconds")
    create_copy_csv_file(csv_file_path, headers_list, rows_list_with_offset)
    print(f"csv file created at {time.time() - start_time} seconds")
    print(f"total time: {time.time() - start_time} seconds")


# if __name__ == "__main__":
#     files_path, header, rows = get_csv_data(path)
    # print(header)
    # print(rows)