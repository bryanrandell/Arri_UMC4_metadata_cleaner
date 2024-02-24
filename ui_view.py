from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QDialog, QFileDialog, QApplication, QComboBox
import csv_lds_reader
import rename_and_edit_csv_by_tc
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV UMC4 METADATA UTILITY")
        self.main_widget = QVBoxLayout()
        self.setLayout(self.main_widget)

        self.button_select_csv = QPushButton("Import UMC4 META csv file")
        self.button_select_csv.clicked.connect(self.import_umc4_csv_file)

        self.button_select_folder = QPushButton("Import Master Folder")
        self.button_select_folder.clicked.connect(self.import_folder)


        self.label_start_tc = QLabel("")
        self.label_total_frame = QLabel("")

        self.label_csv_copy = QLabel('Select folder and Launch csv copy')
        self.main_widget.addWidget(self.label_csv_copy)

        self.layout_select_day_folder = QHBoxLayout()
        self.combo_folder_day = QComboBox()
        self.button_launch_csv_copy = QPushButton("Launch csv copy")
        self.button_launch_csv_copy.clicked.connect(self.launch_copy_csv)
        self.layout_select_day_folder.addWidget(self.combo_folder_day)
        self.layout_select_day_folder.addWidget(self.button_launch_csv_copy)

        self.main_widget.addLayout(self.layout_select_day_folder)
        self.main_widget.addWidget(self.button_select_folder)
        self.main_widget.addWidget(self.button_select_csv)
        self.main_widget.addWidget(self.label_start_tc)
        self.main_widget.addWidget(self.label_total_frame)

        self.label_check_copy_title = QLabel("Copy Check :")
        self.label_check_copy = QLabel("")
        self.main_widget.addWidget(self.label_check_copy_title)
        self.main_widget.addWidget(self.label_check_copy)


    def import_umc4_csv_file(self):
        csv_file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', './')
        header, rows = csv_lds_reader.convert_csv_to_list(csv_file_path)
        start_tc = csv_lds_reader.extract_start_tc(rows)
        total_frame = csv_lds_reader.extract_total_frames(rows)
        self.label_start_tc.setText(start_tc)
        self.label_total_frame.setText(total_frame)

    def import_silverstack_csv_file(self):
        csv_file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', './')
        header, rows = csv_lds_reader.convert_csv_to_list(csv_file_path)
        start_tc = csv_lds_reader.extract_start_tc(rows)
        total_frame = csv_lds_reader.extract_total_frames(rows)
        self.label_start_tc.setText(start_tc)
        self.label_total_frame.setText(total_frame)

    def import_folder(self):
        self.master_folder_path = QFileDialog.getExistingDirectory(self, 'Browse Master Dir', '/Volumes')
        self.day_folder_list = [os.path.join(self.master_folder_path, i) for i in os.listdir(self.master_folder_path)\
                                if os.path.isdir(os.path.join(self.master_folder_path, i)) and not i.startswith(".")]
        self.create_rows()

    def create_rows(self):
        self.combo_folder_day.clear()
        for day_folder in self.day_folder_list:
            self.combo_folder_day.addItem(day_folder)

    def launch_copy_csv(self):
        path = self.combo_folder_day.currentText()
        self.label_check_copy.setText(path)
        # rename_and_edit_csv_by_tc.main(path, path)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
