import pandas as pd
import os


def create_dict_from_silverstack_csv(silverstack_csv_path: str) -> dict:
    """
    >> caution csv exported from silverstack is ";" delimited
    from silverstack ->
    column -> 0: "Name", 1: "Frames", 2: "TC Start", 3: "TC End", 4: "Sensor FPS" (useless?), 5: "Project FPS"
    :param silverstack_csv_path:
    :return:
    """
    data_frame = pd.read_csv(silverstack_csv_path, delimiter=";")
    dict_silverstack_tc_frames = {}
    for data_by_clip in data_frame.values:
        clip_name = data_by_clip[0] #Name
        # get rid of the . at the end of tc from silverstack
        video_start_timecode = ":".join(data_by_clip[2].split('.'))
        video_end_timecode = ":".join(data_by_clip[3].split('.'))
        video_total_frames = data_by_clip[1]
        video_frame_rate = round(float(data_by_clip[5]))
        dict_tc_frames = {"start TC": video_start_timecode, "frames": video_total_frames,
                          "end TC": video_end_timecode, "frame rate": video_frame_rate, "camera index": clip_name[0]}
        dict_silverstack_tc_frames[clip_name] = dict_tc_frames
    return dict_silverstack_tc_frames

