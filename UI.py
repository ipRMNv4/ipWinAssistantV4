import webbrowser

import ollama
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
from PyQt5.QtCore import QTime, QTimer, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QTextOption, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit, QWidget, QSlider, QVBoxLayout, QCalendarWidget
from main import *
import os
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import wmi
from datetime import datetime
# from sptoyt import *

class Worker(QThread):
    finished = pyqtSignal(str)  

    def __init__(self, userquestion):
        super().__init__()
        self.userquestion = userquestion

    def run(self):
        aimodel = 'llama3.2:latest'
        response = ollama.chat(
            model=aimodel,
            messages=[
                {
                    'role': 'user',
                    'content': self.userquestion
                },
            ],
        )
        OllamaResponse = response['message']['content']
        self.finished.emit(OllamaResponse)


class VolumeControl(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_interface = self.get_audio_interface()
        self.init_ui()
        if self.audio_interface:
            initial_volume = self.get_volume()
            self.slider.setValue(initial_volume)

    def init_ui(self):

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.valueChanged.connect(self.on_slider_change)


        # self.label = QLabel("Volume: " + str(self.slider.value()) + "%", self)


        layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)


        self.setWindowTitle('Volume Control')

        # self.setGeometry(100, 100, 300, 100)
        # self.setGeometry(80, 50, 150, 20)
        # self.hide()

    def on_slider_change(self):

        value = self.slider.value()

        self.set_volume(value)

    def get_audio_interface(self):

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = interface.QueryInterface(IAudioEndpointVolume)
            return volume
        except Exception as e:
            print("Error accessing audio interface:", e)
            return None

    def set_volume(self, value):

        if self.audio_interface:

            self.audio_interface.SetMasterVolumeLevelScalar(value / 100.0, None)

    def get_volume(self):

        if self.audio_interface:

            return int(self.audio_interface.GetMasterVolumeLevelScalar() * 100)
        return 50

class BrightnessControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Brightness Control")
        # self.setGeometry(100, 100, 300, 100)
        # self.setGeometry(80, 35, 150, 20)  # Slightly move down

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(self.get_brightness())


        self.slider.valueChanged.connect(self.adjust_brightness)


        # self.label = QLabel(f"Brightness: {self.slider.value()}%", self)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        # layout.addWidget(self.label)
        self.setLayout(layout)

    def get_brightness(self):
        w = wmi.WMI(namespace="wmi")
        for monitor in w.WmiMonitorBrightness():
            return monitor.CurrentBrightness

    def adjust_brightness(self):
        brightness_value = self.slider.value()
        w = wmi.WMI(namespace="wmi")
        for monitor in w.WmiMonitorBrightnessMethods():
            monitor.WmiSetBrightness(Brightness=brightness_value, Timeout=0)


class RectangleWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.is_playing = True
        self.time_label = QLabel(self)
        self.time_label.setStyleSheet("font-size: 15px; color: white;")
        self.time_label.setGeometry(610, 10, 130, 30)
        self.update_time()


        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)


        self.setWindowTitle("WINGMAN")
        self.setGeometry(420, 0, 1100, 250)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)


        self.is_hovered = False
        self.rectangle_width = 300
        self.rectangle_height = 30
        self.show_additional_rectangles = False


        self.play_button = QPushButton(self)
        self.previous_button = QPushButton(self)
        self.next_button = QPushButton(self)

        icon_size = 30

        self.previous_button.setIcon(QIcon("wprevious.png"))
        self.play_button.setIcon(QIcon("wplay.png"))
        self.next_button.setIcon(QIcon("wnext.png"))


        self.play_button.setIconSize(QSize(icon_size, icon_size))
        self.previous_button.setIconSize(QSize(20, 20))
        self.next_button.setIconSize(QSize(20, 20))


        self.play_button.setStyleSheet("background-color: transparent; border: none;")
        self.previous_button.setStyleSheet("background-color: transparent; border: none;")
        self.next_button.setStyleSheet("background-color: transparent; border: none;")


        self.play_button.hide()
        self.previous_button.hide()
        self.next_button.hide()


        self.play_button.clicked.connect(self.toggle_playback)
        self.previous_button.clicked.connect(play_previous)
        self.next_button.clicked.connect(play_next)


        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter text here...")
        self.text_input.setGeometry(255, 50, 590, 30)
        self.text_input.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white; border: none;")
        self.text_input.returnPressed.connect(self.run_ai)
        self.text_input.setVisible(False)


        self.output_box = QTextEdit(self)
        self.output_box.setGeometry(255, 80, 590, 160)
        self.output_box.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white; border: none;")
        self.output_box.setReadOnly(True)
        self.output_box.setVisible(False)


        self.output_box.setAlignment(Qt.AlignLeft)
        self.output_box.setWordWrapMode(QTextOption.WordWrap)


        self.text = self.get_currently_playing_text()
        self.font = QtGui.QFont("Arial", 16, QtGui.QFont.Bold)
        self.font_metrics = QtGui.QFontMetrics(self.font)
        self.text_width = self.font_metrics.horizontalAdvance(self.text)


        self.current_x = self.width()


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_marquee)
        self.timer.start(30)


        self.word_timer = QTimer(self)
        self.word_timer.timeout.connect(self.display_next_word)
        self.word_timer.setInterval(20)


        self.song_update_timer = QTimer(self)
        self.song_update_timer.timeout.connect(self.update_song_label)
        self.song_update_timer.start(5000)


        self.link_button = QPushButton("Spotify to YT playlist", self)
        self.link_button.setGeometry(70, 150, 150, 30)
        self.link_button.setStyleSheet("background-color: green; color: white; border-radius: 5px;")
        self.link_button.clicked.connect(self.open_link)
        self.link_button.hide()



        self.date_label = QLabel(self)
        self.date_label.setStyleSheet("font-size: 15px; color: white;")
        self.date_label.setGeometry(410, 10, 200, 30)
        self.date_label.setText(self.get_current_date())



        self.playing_on = QLabel(self)
        self.playing_on.setStyleSheet("font-size: 15px; color: green; font-weight: bold;")
        self.playing_on.setGeometry(875, 70, 200, 30)
        self.playing_on.setText("PLAYING ON SPOTIFY")
        self.playing_on.hide()


        self.volume_control = VolumeControl(self)
        self.volume_control.setGeometry(80, 60, 150, 50)
        self.volume_control.hide()


        self.volume_image_label = QLabel(self)
        self.volume_image_label.setGeometry(60, 65, 40, 40)
        self.volume_image_label.setPixmap(QPixmap("volume_icon.png").scaled(20, 20, QtCore.Qt.KeepAspectRatio))
        self.volume_image_label.setStyleSheet("background-color: transparent;")
        self.volume_image_label.hide()


        self.logo_label = QLabel(self)
        self.logo_label.setGeometry(530, 5, 40, 40)
        self.logo_label.setPixmap(QPixmap("Wingman.png").scaled(20, 20, QtCore.Qt.KeepAspectRatio))
        self.logo_label.setStyleSheet("background-color: transparent;")
        self.logo_label.hide()


        self.BrightnessControl = BrightnessControl(self)
        self.BrightnessControl.setGeometry(80, 95, 150, 50)
        self.BrightnessControl.hide()

        self.brightness_image_label = QLabel(self)
        self.brightness_image_label.setGeometry(60, 100, 40, 40)
        self.brightness_image_label.setPixmap(QPixmap("brightness_icon.png").scaled(20, 20, QtCore.Qt.KeepAspectRatio))
        self.brightness_image_label.setStyleSheet("background-color: transparent;")
        self.brightness_image_label.hide()

    def open_link(self):
        path = r"D:\PROJECTS\WINGMAN\index3.html"
        webbrowser.open(path)

    def get_current_date(self):

        return datetime.now().strftime("%a, %b %d, %Y")

    def toggle_playback(self):
            if self.is_playing:
                pause_playback()
                self.is_playing = False
            else:
                resume_playback()
                self.is_playing = True

    def update_song_label(self):
        current_song = self.get_currently_playing_text()
        if current_song != self.text:
            self.text = current_song
            self.text_width = self.font_metrics.horizontalAdvance(self.text)
            self.update()

    def get_currently_playing_text(self):

        return currently_playing()

    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss AP")
        self.time_label.setText(current_time)



    def run_ai(self):
        userquestion = self.text_input.text()
        self.text_input.clear()


        if userquestion.lower() == "open youtube":
            self.output_box.setText("Opening YouTube...")
            webbrowser.open("https://www.youtube.com")

        elif userquestion.lower() == "open spotify":
            self.output_box.setText("Opening Spotify...")
            open_spotify()

        elif userquestion.lower().startswith("notes"):
            self.save_note(userquestion)

        elif userquestion.startswith("https://"):
            download_status = download_file(userquestion)
            self.output_box.setText(download_status)

        else:

            self.worker = Worker(userquestion)
            self.worker.finished.connect(self.prepare_response)
            self.worker.start()

    def save_note(self, userquestion):
        time = datetime.now()
        formatted_time = time.strftime("%d/%m/%Y %H:%M:%S")
        note = userquestion.replace("notes", "", 1).strip()
        try:

            folder_path = r"C:\NOTES"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(r"C:\NOTES\notes.txt", "a") as f:
                f.write(f"{formatted_time}:\n{note} \n")
            self.output_box.setText("Note saved.")

        except Exception as e:

            print(f"Error saving note: {e}")
            self.output_box.setText(f"Error saving note: {e}")


    def prepare_response(self, response):
        self.words = response.split()
        self.current_word_index = 0
        self.output_box.clear()
        self.word_timer.start(1)

    def display_next_word(self):
        if self.current_word_index < len(self.words):
            self.output_box.insertPlainText(self.words[self.current_word_index] + ' ')
            self.current_word_index += 1
        else:
            self.word_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)


        x = (self.width() - self.rectangle_width) // 2
        y = 10

        if self.is_hovered:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor(0, 0, 0, 255))
            self.rectangle_width = 600
            rectangle_rect = QtCore.QRect(x, y, self.rectangle_width, self.rectangle_height)
            painter.drawRoundedRect(rectangle_rect, 10, 10)
            self.show_additional_rectangles = True
        else:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor(0, 0, 0, 150))
            self.rectangle_width = 300
            rectangle_rect = QtCore.QRect(x, y, self.rectangle_width, self.rectangle_height)
            painter.drawRect(rectangle_rect)
            self.show_additional_rectangles = False


        if self.show_additional_rectangles:
            additional_rect_width = 600
            additional_rect_height = 200
            corner_radius = 15
            rect1_x = x
            rect2_x = x + self.rectangle_width
            rect3_x = x - 200
            additional_y = y + self.rectangle_height

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor(0, 0, 0, 150))
            painter.drawRoundedRect(QtCore.QRect(rect1_x, additional_y, additional_rect_width, additional_rect_height), corner_radius, corner_radius)
            painter.drawRoundedRect(QtCore.QRect(rect3_x, 50, 200, 170), corner_radius, corner_radius)



            ellipse_rect = QtCore.QRect(rect2_x, 20, 220, 220)
            painter.setBrush(QtGui.QColor(0, 0, 0, 150))
            painter.drawEllipse(ellipse_rect)


            painter.setClipRegion(QtGui.QRegion(ellipse_rect))
            painter.setFont(self.font)
            painter.setPen(QtCore.Qt.white)
            text_y_position = ellipse_rect.center().y() + self.font_metrics.ascent() // 2


            painter .drawText(self.current_x, text_y_position, self.text)

            button_offset_y = 150
            button_spacing = 50
            self.previous_button.setGeometry(rect2_x + 40, 20 + button_offset_y, 30, 30)
            self.play_button.setGeometry(rect2_x + 40 + button_spacing, 20 + button_offset_y, 30, 30)
            self.next_button.setGeometry(rect2_x + 40 + 2 * button_spacing, 20 + button_offset_y, 30, 30)

    def update_marquee(self):

        self.current_x -= 1


        x = (self.width() - self.rectangle_width) // 2
        ellipse_rect = QtCore.QRect(x + self.rectangle_width, 20, 220, 220)

        if self.current_x + self.text_width < ellipse_rect.left():
            self.current_x = self.width()

        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.play_button.show()
        self.previous_button.show()
        self.next_button.show()

        self.text_input.setVisible(True)
        self.output_box.setVisible(True)
        self.time_label.setGeometry(750, 10, 130, 30)

        self.volume_control.show()
        self.BrightnessControl.show()
        self.volume_image_label.show()
        self.brightness_image_label.show()


        self.logo_label.show()
        self.date_label.setGeometry(260, 10, 200, 30)
        # self.date_label.setText(self.get_current_date())  # Update date
        self.playing_on.show()
        self.link_button.show()

        self.update()

    def leaveEvent(self, event):
        self.is_hovered = False
        self.play_button.hide()
        self.previous_button.hide()
        self.next_button.hide()

        self.text_input.setVisible(False)
        self.output_box.setVisible(False)
        self.time_label.setGeometry(610, 10, 130, 30)

        self.volume_control.hide()
        self.BrightnessControl.hide()
        self.volume_image_label.hide()
        self.brightness_image_label.hide()
        # self.date_label.hide()
        self.date_label.setGeometry(410, 10, 200, 30)
        self.logo_label.hide()
        self.playing_on.hide()
        self.link_button.hide()
        self.update()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = RectangleWidget()
    widget.show()
    sys.exit(app.exec_())
