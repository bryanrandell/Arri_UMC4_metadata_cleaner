import csv_lds_reader as csv_read
from ffmpeg_command_probe import create_dict_meta_for_video_in_day_folder
import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QFileDialog, QApplication, QHBoxLayout, QVBoxLayout, QCheckBox

sd_card_path = "/Volumes/NO NAME"
day_folder_path = '/Volumes/NVME_02/TNL/DAY_107'
report_csv_silverstack_path = '/Volumes/NVME_02/TNL/DAY_107/REPORTS/DAY_107.csv'

def find_correponding_meta_with_tc_and_cam_index(shooting_day_folder_path: str) -> dict:
    """
    compare tc from csv to tc from video with same reel name, then make a copy to the csv file including
    video filename in prefix and crop rows with tc anterior to the start tc video
    :param shooting_day_folder_path:
    :return: dict
    """
    # using set to eliminate duplicate reel names
    dict_video_meta_correspondance = {}
    dict_video_tc_frame_path = create_dict_meta_for_video_in_day_folder(shooting_day_folder_path)
    extracted_reel = {i[:4] for i in dict_video_tc_frame_path.keys()}
    print(f" reel {extracted_reel}")

    dict_csv_meta = get_meta_from_sd_card(shooting_day_folder_path)
    for reel in extracted_reel:
        csv_folder_path = ""
        for root, dirs, files in os.walk(shooting_day_folder_path):
            for dir in dirs:
                if dir.find(reel) != -1 and dir.endswith("META"):
                    csv_folder_path = os.path.join(shooting_day_folder_path, f"METADATA/{dir}")
        print(f"csv_folder_path {csv_folder_path}")
        for csv_file in os.listdir(csv_folder_path):
            if csv_file.endswith(".csv"):
                header, rows = csv_read.convert_csv_to_list(os.path.join(csv_folder_path, csv_file))
                csv_cam_index = csv_read.extract_camera_index(rows, header)
                csv_start_tc = csv_read.extract_start_tc(rows, header)
                csv_start_tc_in_frames = csv_read.convert_tc_to_frames(csv_start_tc)
                csv_total_frames = csv_read.extract_total_frames(rows)
                range_tc_csv = {i for i in range(csv_start_tc_in_frames, csv_start_tc_in_frames + csv_total_frames)}
                for video_key in dict_video_tc_frame_path.keys():
                    video_cam_index = dict_video_tc_frame_path[video_key]["camera index"]
                    video_start_tc = dict_video_tc_frame_path[video_key]["start TC"]
                    video_start_tc_in_frames = csv_read.convert_tc_to_frames(video_start_tc)
                    video_total_frames = dict_video_tc_frame_path[video_key]["frames"]
                    range_tc_video = {i for i in range(video_start_tc_in_frames, video_start_tc_in_frames + video_total_frames)}
                    if range_tc_csv.intersection(range_tc_video) and csv_cam_index == video_cam_index:
                        # make a copy of the csv file including video filename in prefix and crop rows with tc anterior to the start tc video
                        csv_file_path = os.path.join(csv_folder_path, csv_file)
                        video_file_path = dict_video_tc_frame_path[video_key]["file path"]
                        dict_video_meta_correspondance[video_file_path] = csv_file_path
                    else:
                        print(f"{csv_file} is not copied cause index or tc is not matching to {video_key}")
            else:
                print(f"{csv_file} is not a csv file")
    return dict_video_meta_correspondance


def get_clip_tc_from_silverstack_csv():
    pass


def get_meta_from_sd_card(meta_path: str, path_sd_card: bool=False) -> dict:
    # csv_root_path = "/Volumes/No\ Name/"
    csv_root_path = ""
    if path_sd_card:
        csv_root_path = "/Volumes/No Name/"
        for root, dirs, files in os.walk(csv_root_path):
            for dir in dirs:
                if dir == "0001":
                    csv_root_path = os.path.join(root, dir)
    else:
        reel = os.path.basename(meta_path)[:4]
        csv_root_path = "/".join(meta_path.split("/")[:-2] + ["METADATA", f"{reel}_META"])


    csv_file_list = [file for file in os.listdir(csv_root_path) if file.endswith(".csv")]
    csv_meta_dict = {}
    for csv_file in csv_file_list:
        param_csv_dict = {}
        header, rows = csv_read.convert_csv_to_list(os.path.join(csv_root_path, csv_file))
        param_csv_dict["total frames"] = csv_read.extract_total_frames(rows)
        param_csv_dict["start TC"] = csv_read.extract_start_tc(rows, header)
        param_csv_dict["cam index"] = csv_read.extract_camera_index(rows, header)
        csv_meta_dict[csv_file] = param_csv_dict

    return csv_meta_dict


def compare_meta_dict_to_video_clip(csv_meta_dict: dict, dict_mxf_tc_frames: dict) -> dict:
    print(csv_meta_dict)
    print(f" len meta dict : {len(csv_meta_dict)}")
    print(f"len video dict : {len(dict_mxf_tc_frames)}")
    total_clip_diff = len(csv_meta_dict) - len(dict_mxf_tc_frames)
    dict_diff = {"total clips difference": total_clip_diff}
    for key_video, key_meta in zip(dict_mxf_tc_frames.keys(), csv_meta_dict.keys()):
        csv_frames = int(csv_meta_dict[key_meta]["total frames"])
        video_frames = int(dict_mxf_tc_frames[key_video]["frames"])
        csv_start_tc = csv_read.convert_tc_to_frames(csv_meta_dict[key_meta]["start TC"])
        video_start_tc = csv_read.convert_tc_to_frames(dict_mxf_tc_frames[key_video]["start TC"])
        dict_diff[f"{key_video}-{key_meta}"] = {
            "total frames difference": csv_frames - video_frames,
            "start TC difference": csv_start_tc - video_start_tc,
            "end TC difference": (csv_start_tc + csv_frames) - (video_start_tc + video_frames)
        }

    return dict_diff


class CompareWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Check Meta Integrity")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.search_meta_in_sd = False

        self.button_launch_check = QPushButton("Select Video Folder and check meta")
        self.button_launch_check.clicked.connect(self.select_video_reel_folder_and_check_meta)

        self.label_layout = QVBoxLayout()

        self.box_metadata_location = QCheckBox("Meta in SD Card")
        self.box_metadata_location.stateChanged.connect(self.check_meta_in_sd_card)


        self.main_layout.addWidget(self.button_launch_check)
        self.main_layout.addWidget(self.box_metadata_location)
        self.main_layout.addLayout(self.label_layout)

    def check_meta_in_sd_card(self):
        if self.box_metadata_location.isChecked():
            self.search_meta_in_sd = True
        else:
            self.search_meta_in_sd = False

    def select_video_reel_folder_and_check_meta(self):
        video_folder_path = QFileDialog.getExistingDirectory(self, "Select Video Folder")
        dict_meta = get_meta_from_sd_card(video_folder_path, self.search_meta_in_sd)
        dict_video_tc_frame_path = create_dict_meta_for_video_in_day_folder(video_folder_path)
        dict_compare_meta_video = compare_meta_dict_to_video_clip(dict_meta, dict_video_tc_frame_path)

        for i in dict_compare_meta_video:
            self.label = QLabel(f"{i} {dict_compare_meta_video[i]}")
            self.label_layout.addWidget(self.label)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CompareWindow()
    win.show()
    sys.exit(app.exec_())






