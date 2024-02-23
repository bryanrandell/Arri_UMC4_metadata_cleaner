import os
import shutil
import csv_lds_reader as csv_read
from ffmpeg_command_probe import create_dict_meta_for_video_in_day_folder
from silverstack_csv_reader import create_dict_from_silverstack_csv

# todo make 2 versions by detection video or silverstack csv


def comparing_csv_tc_with_video_files(dict_video_tc_frame_path: dict, shooting_day_folder_path: str,
                                      csv_sub_folder: str = "METADATA",
                                      sub_folder_creation_name: str = "RENAMED_AND_RESYNCED_META",
                                      create_sub_folder: bool = True, add_dummy_rows: bool = False) -> None:
    """
    # todo this function is too long parse it into smaller fonction, easier to understand
    compare tc from csv to tc from video with same reel name, then make a copy to the csv file including
    video filename in prefix and crop rows with tc anterior to the start tc video
    # todo : implement a dummy row to add row at the end of csv corresponding to end TC
    :param dict_video_tc_frame_path:
    :param dict_video_tc_frame_path, shooting_day_folder_path:
    :return: None
    """
    # using set to eliminate duplicate reel names
    # usefull to sort reel items
    extracted_reel = sorted({i[:4] for i in dict_video_tc_frame_path.keys()})
    print(f"reel {extracted_reel}")
    for reel in extracted_reel:
        csv_folder_path = ""
        for root, dirs, files in os.walk(shooting_day_folder_path):
            for dir in dirs:
                if dir.find(reel) != -1 and dir.endswith("META"):
                    csv_folder_path = os.path.join(shooting_day_folder_path, f"{csv_sub_folder}/{dir}")
        print(f"csv_folder_path = {csv_folder_path}")
        if csv_folder_path == "":
            print(f"Cannot find META folder for reel {reel}, please check your meta, continuing to next reel")
            continue
        for csv_file in os.listdir(csv_folder_path):
            if csv_file.endswith(".csv"):
                # todo replace csv_reader by pandas lib
                header, rows = csv_read.convert_csv_to_list(os.path.join(csv_folder_path, csv_file))
                csv_cam_index = csv_read.extract_camera_index(rows, header)
                csv_start_tc = csv_read.extract_start_tc(rows, header)
                csv_start_tc_in_frames = csv_read.convert_tc_to_frames(csv_start_tc)
                csv_total_frames = csv_read.extract_total_frames(rows)
                range_tc_csv = {i for i in range(csv_start_tc_in_frames, csv_start_tc_in_frames + csv_total_frames)}
                for video_key in dict_video_tc_frame_path.keys():
                    video_cam_index = dict_video_tc_frame_path[video_key]["camera index"]
                    video_start_tc = dict_video_tc_frame_path[video_key]["start TC"]
                    video_end_tc = dict_video_tc_frame_path[video_key]["end TC"]
                    video_start_tc_in_frames = csv_read.convert_tc_to_frames(video_start_tc)
                    video_end_tc_in_frames = csv_read.convert_tc_to_frames(video_end_tc)
                    # video_total_frames = dict_video_tc_frame_path[video_key]["frames"]
                    # range_tc_video = {i for i in range(video_start_tc_in_frames, video_start_tc_in_frames + video_total_frames)}
                    # for csv from silverstack yuo have access to end TC
                    range_tc_video = {i for i in range(video_start_tc_in_frames, video_end_tc_in_frames)}
                    if range_tc_csv.intersection(range_tc_video) and csv_cam_index == video_cam_index:
                        # make a copy of the csv file including video filename in prefix and crop rows with tc anterior to the start tc video
                        csv_file_path = os.path.join(csv_folder_path, csv_file)
                        # video_file_path_from_dict = dict_video_tc_frame_path[video_key]["file path"]
                        # video_file_name = os.path.basename(video_file_path_from_dict)
                        video_file_name = video_key
                        # can be add to function parameters
                        sub_folder = sub_folder_creation_name
                        csv_subfolder_path = os.path.join(csv_folder_path, sub_folder)
                        if create_sub_folder:
                            if not os.path.exists(csv_subfolder_path):
                                os.mkdir(csv_subfolder_path)
                            new_csv_file_path = os.path.join(csv_subfolder_path, f"{video_file_name}_{csv_file}")
                        else:
                            new_csv_file_path = os.path.join(csv_folder_path, f"{video_file_name}_{csv_file}")
                        file_path = csv_read.crop_csv_file_with_tc(csv_file_path, new_csv_file_path, video_start_tc_in_frames)
                        # todo calculate the difference of tc between video and csv and create rows at the end of csv file
                        #  to match the total frame count
                        print(f"{csv_file} is copied to {new_csv_file_path}")
                    else:
                        print(f"{csv_file} is not copied cause index or tc is not matching to {video_key}")
            else:
                print(f"{csv_file} is not a csv file")


def extract_metadata_modified(path_to_all_shooting_days: str, copy_path: str,
                              folder_name: str = "RENAMED_AND_RESYNCED_META", with_day_subfolder: bool = True) -> None:
    """
    extract metadata from all the shooting days and copy them to a new folder
    :param with_day_subfolder:
    :param path_to_all_shooting_days:
    :param copy_path:
    :param folder_name:
    :return: None
    """
    for root, dirs, files in os.walk(path_to_all_shooting_days):
        for dir in dirs:
            if dir.find(folder_name) != -1:
                csv_folder_path = os.path.join(root, dir)
                for csv_file in os.listdir(csv_folder_path):
                    if csv_file.endswith(".csv"):
                        csv_file_path = os.path.join(csv_folder_path, csv_file)
                        if with_day_subfolder:
                            # shooting_day_subfolder = csv_file_path.split("/")[-4]
                            # alternative way to get the shooting day subfolder name with find method
                            shooting_day_subfolder = [i for i in csv_file_path.split("/") if i.find("DAY_") != -1][0]
                            subfolder_path = os.path.join(copy_path, shooting_day_subfolder)
                            if not os.path.exists(subfolder_path):
                                os.mkdir(subfolder_path)
                            new_csv_file_path = os.path.join(subfolder_path, csv_file)
                        else:
                            new_csv_file_path = os.path.join(copy_path, csv_file)
                        shutil.copy(csv_file_path, new_csv_file_path)
                        print(f"{csv_file} is copied to {new_csv_file_path}")
                    else:
                        print(f"{csv_file} is not a csv file")



# todo the path could be redondant, check if only one path from the shooting day would suffice
# iterate over all the folder days
def main_edit_UMC_csv_from_silverstack_csv(day_of_shooting_folder_path: str = "METADATA/") -> None:
    dict_silverstack = create_dict_from_silverstack_csv(silverstack_csv)
    comparing_csv_tc_with_video_files(dict_silverstack, day_of_shooting_folder_path)

def main_edit_UMC_csv_from_video_files(day_of_shooting_folder_path: str = "METADATA/") -> None:
    dict_video = create_dict_meta_for_video_in_day_folder(day_of_shooting_folder_path)
    comparing_csv_tc_with_video_files(dict_video, day_of_shooting_folder_path)


if __name__ == "__main__":
    # dict_test = {'C102C001_2207262N': {'startTC': '17:17:10:14', 'frames': 8172,
    #                                    'file path': 'VIDEO/C102CSQE/C102CSQE/Clip/C102C001_2207262N/C102C001_2207262N.mxf'}}
    # video_file_path = "VIDEO/C102CSQE"
    day_of_shooting_folder_path = "DAY_061/"
    silverstack_csv = "csv_silverstack/DAY_061.csv"
    # main_edit_UMC_csv_from_video_files(video_file_path, day_of_shooting_folder_path)
    main_edit_UMC_csv_from_silverstack_csv(day_of_shooting_folder_path)
