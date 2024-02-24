"""
get a dict for changing meta from a video by copying the codec from ffmpeg and add metadata argument
"""

import subprocess

ffmpeg = "/usr/local/bin/ffmpeg"
json_dir = "/Users/bryanrandell/PycharmProjects/csv_lcs_reaader/json_files"

from typing import NamedTuple
import json


class FFProbeResult(NamedTuple):
    return_code: int
    json_str: str
    error: str
    converted_json: dict


def ffprobe(file_path) -> FFProbeResult:
    command_array = ["ffprobe",
                     "-v", "quiet",
                     "-print_format", "json",
                     "-show_format",
                     "-show_streams",
                     file_path]
    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return FFProbeResult(return_code=result.returncode,
                         json_str=result.stdout,
                         error=result.stderr,
                         converted_json=json.loads(result.stdout))


def grabUserInput():
    path = "/Users/bryanrandell/Movies/export_test/"
    input_file = "Untitled.mov"
    output_file = "Untitled_copy.mov"
    new_timecode = "01:00:00:01"
    video_change_timecode_dict = {}

    video_change_timecode_dict["input_file"] = "{}{}".format(path, input_file)
    video_change_timecode_dict["output_file"] = "{}{}".format(path, output_file)
    video_change_timecode_dict["timecode"] = 'timecode="{}"'.format(new_timecode)

    return video_change_timecode_dict


def depreciated_build_ffmpeg_command(video_change_timecode_dict=grabUserInput()):
    """
    build the command line for ffmpeg
    :param video_change_timecode_dict:
    :return:
    """
    commands_list = [
        ffmpeg,
        "-i",
        video_change_timecode_dict["input_file"],
        "-metadata",
        video_change_timecode_dict["timecode"],
        "-codec",
        "copy",
        video_change_timecode_dict["output_file"],
        "&&",
        video_change_timecode_dict["output_file"],
        video_change_timecode_dict["input_file"]
    ]

    return commands_list


def build_ffmpeg_Command(temp_file_path, timecode):
    """
    build the command line for ffmpeg
    :param video_change_timecode_dict:
    :return:
    """
    output_file_path = temp_file_path.split("_temp_")[0] + temp_file_path.split("_temp_")[1]
    commands_list = [
        ffmpeg,
        "-i",
        temp_file_path,
        "-metadata",
        'timecode={}'.format(timecode),
        "-codec",
        "copy",
        output_file_path
    ]

    return commands_list


def buildFFprobeCommand(video_path):
    """
    Get video timecode with ffprobe
    ffprobe -v quiet -print_format json -show_format -show_streams "lolwut.mp4" > "lolwut.mp4.json"
    :param
    :param video_path:
    :return:
    """
    import os

    commands_list = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        video_path,
        ">",
        "{}/{}.{}".format(json_dir, os.path.basename(video_path), "json")
    ]

    return commands_list


def buildFFmpegCommandAudio(temp_file_path, timecode):
    """
    build the command line for ffmpeg
    :param video_change_timecode_dict:
    :return:
    """
    output_file_path = temp_file_path.split("_temp_")[0] + temp_file_path.split("_temp_")[1]
    commands_list = [
        ffmpeg,
        "-i",
        temp_file_path,
        "-metadata",
        'timecode={}'.format(timecode),
        "-f",
        "mxf_opatom",
        output_file_path
    ]

    return commands_list


def runFFmpeg(commands):
    """
    run the ffmpeg in the terminal
    :param commands:
    :return:
    """

    print(commands)
    if subprocess.run(commands).returncode == 0:
        print ("FFmpeg Script Ran Successfully")
    else:
        print ("There was an error running your FFmpeg script")


def runFFprobeAndGetJson(commands):
    """
    run the ffprobe in the terminal
    :param commands:
    :return:
    """
    print(commands)
    if subprocess.run(commands).returncode == 0:
        print ("FFprobe Script Ran Successfully")
        # return subprocess.Popen(commands, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    else:
        print ("There was an error running your FFprobe script")


def create_dict_meta_for_video_in_day_folder(day_path: str = "Other_code_with_umc4_to_nuke/C102CSQE", sub_folder_name ="Other_code_with_umc4_to_nuke") -> dict:
    """
    main function, enter a directory and get the start tc and total frames of the video file
    :return: timecode and frame duration with ffprobe command
    """
    # video_path = "Other_code_with_umc4_to_nuke/C102CSQE"
    dict_mxf_tc_frames = {}
    import os
    for root, dir, files in os.walk(os.path.join(day_path, sub_folder_name)):
        for file in files:
            if file.endswith(".mxf"):
                video_file_path = os.path.join(root, file)

    # command = buildFFprobeCommand(list_mxf[0])
    # json_file_path = command[-1]
    # runFFprobeAndGetJson(command)
    # ffmpeg = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                result = ffprobe(video_file_path)
                print("out: {}".format(result.converted_json))
    # print("err: {}".format(err))

    # # json file location defined in ffprobe command
    # with open(json_file_path, "r") as file:
    #     json_file = json.load(file)
    #     video_timecode = json_file["format"]["tags"]["timecode"]
    #     video_total_frames = json_file["streams"][0]["duration_ts"]
                video_start_timecode = result.converted_json["format"]["tags"]["timecode"]
                video_total_frames = result.converted_json["streams"][0]["duration_ts"]
                string_frame_rate = result.converted_json["streams"][0]['time_base']
                video_frame_rate = round(int(string_frame_rate.split('/')[0]) / int(string_frame_rate.split('/')[1]))

                dict_tc_frames = {"start TC": video_start_timecode, "frames": video_total_frames,
                                  "file path": video_file_path, "frame rate": video_frame_rate, "camera index": file[0]}
                dict_mxf_tc_frames[file.split(".")[0]] = dict_tc_frames
    return dict_mxf_tc_frames


if __name__ == "__main__":
    dict_mxf_tc_frames = create_dict_meta_for_video_in_day_folder()
    print(f"video_start_timecode = {dict_mxf_tc_frames['C102C001_2207262N']}, video_total_frames = {dict_mxf_tc_frames['C102C001_2207262N']}")

# if __name__ == "__main__":
#     runFFmpeg(buildFFmpegCommand())
#     video_path = "Other_code_with_umc4_to_nuke/C102CSQE"
#     list_mxf = []
#     import os
#     import json
#
#     for root, dir, files in os.walk(video_path):
#         for file in files:
#             if file.endswith(".mxf"):
#                 list_mxf.append(os.path.join(root, file))
#
#     runFFprobeAndGetJson(buildFFprobeCommand(list_mxf[0]))
#     # json file location defined in ffprobe command
#     json_file = "{}.{}".format(list_mxf[0].split(".")[0], "json")
#
#     with open(list_mxf[0].split(".")[0] + ".json", "r") as f:
#         json_file = json.load(f)
#         video_timecode = json_file["format"]["tags"]["timecode"]
#         video_total_frames = json_file["streams"][0]["duration_ts"]
#
