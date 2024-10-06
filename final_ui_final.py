from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PyQt5.QtGui.QIcon import pixmap
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
import psutil
import sys
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, QSize
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QTextEdit
from prototype_functional import CommandApp
import os
import webbrowser
import requests
import google.generativeai as genai
import schedule
import time
import re
import psutil
import subprocess
import notes
from download import download_file
from spotify_to_yt import final
from main import *
from main import pause_playback
from main import resume_playback
from main import play_next
from main import play_previous
from main import playback_state
from main import currently_playing
import google.generativeai as genai
genai.configure(api_key='AIzaSyBYkElOybiQw0VyRkr8w-l-PS4-0gzzOoI')
resultt = playback_state()

class ToolBar(QWidget):
    def __init__(self):
        super(ToolBar, self).__init__()

        self.is_playing = True
        # Window size
        self.w = 400
        self.w1 = 1200
        self.h = 50
        self.h1 = 200  # Increased height to accommodate input box + output area
        self.resize(self.w, self.h)

        # Widget
        self.centralwidget = QWidget(self)
        self.centralwidget.resize(self.w1, self.h1)

        # Initial
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.initial_size = QSize(self.w, self.h)
        self.hover_size = QSize(self.w1, self.h1)

        self.set_stylesheet(self.h / 2)
        screen = QApplication.primaryScreen()
        screenSize = screen.geometry()
        self.getCentered = int((screenSize.width() / 2) - (self.w / 2))
        self.setGeometry(self.getCentered, 10, self.w, self.h)

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)  # Update every second

        # timer = QTimer(self)
        # timer.timeout.connect(currently_playing())
        # timer.start(1000)  # Update every second

        font_path = r"G:\My Drive\WINGMAN\fonts\SixtyfourConvergence-Regular.ttf"  # Update with the actual path to your font file
        font_id = QFontDatabase.addApplicationFont(font_path)

        # Get the font family name (usually the first in the list)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = 'Arial'  # Fallback to Arial if loading fails

        # Set up the label
        self.song_label = QLabel(self)
        self.song_label.setGeometry(QRect(850, 50, 600, 18))

        # Apply custom font using font-family in the stylesheet
        self.song_label.setStyleSheet(f"background-color: transparent; color: #FFFFFF; font-family: '{font_family}'; font-size: 14px; font-weight: bold; padding: 0;")

        self.song_label.setText(f"playing: {currently_playing()}")

        self.marquee_animation = QPropertyAnimation(self.song_label, b"pos")

        self.marquee_animation.setDuration(5000)  # animation duration in milliseconds

        self.marquee_animation.setStartValue(QPoint(850, 50))  # start at the initial position of the QLabel

        self.marquee_animation.setEndValue(QPoint(600,50))  # end at the position where the text is off the screen

        self.marquee_animation.setLoopCount(-1)  # loop indefinitely

        self.marquee_animation.start()




        # Add CommandApp widget (the input box) below Spotify icon
        self.command_app = CommandApp(output_widget=None, toolbar=self)  # Pass toolbar reference for expansion
        self.command_app.setParent(self)
        self.command_app.setGeometry(QRect(15, 40, 350, 30))  # Position under the Spotify icon
        self.command_app.hide()  # Hide initially until enterEvent is triggered

        # Add QTextEdit widget (output area) below the input box
        self.output_area = QTextEdit(self)
        self.output_area.setGeometry(QRect(15, 80, 750, 80))  # Position below the input box
        self.output_area.setStyleSheet("background-color: black; color: white; border: none;")
        self.output_area.setReadOnly(True)  # Output area is not editable
        self.output_area.hide()  # Hide initially

        self.label = QLabel(self)
        self.label.setStyleSheet("background-color:transparent;color: #FFFFFF;font-family: 'Arial'; font-size: 14px; font-weight: bold; padding: 0;")
        self.label.setGeometry(QRect(15, 40, 1050, 30))

        icon_size = 30  # Size for each icon button
        x_offset = 950  # Position to the right of the output area (15 + 350 + spacing)
        y_position = 90  # Same y-position as the output area

        # First button (Icon 1)
        self.icon1_button = QPushButton(self)

        self.icon1_button.setGeometry(QRect(x_offset + icon_size + 10, y_position, icon_size, icon_size))
        self.icon1_button.setIcon(QIcon("wplay.png"))
        self.icon1_button.setIconSize(QSize(icon_size, icon_size))
        self.icon1_button.setStyleSheet("background-color: transparent; border: none;")  # No background or border
        self.icon1_button.clicked.connect(self.toggle_playback)  # Connect to a function



        # Second button (Icon 2)
        self.icon2_button = QPushButton(self)
        self.icon2_button.setGeometry(QRect(x_offset + 2 * (icon_size + 10), y_position, icon_size, icon_size))  # Spacing between buttons
        self.icon2_button.setIcon(QIcon("wnext.png"))  # Set your second icon here
        self.icon2_button.setIconSize(QSize(20, 20))
        self.icon2_button.setStyleSheet("background-color: transparent; border: none;")
        self.icon2_button.clicked.connect(play_previous)  # Connect to a function

        # Third button (Icon 3)
        self.icon3_button = QPushButton(self)
        self.icon3_button.setGeometry(QRect(x_offset, y_position, icon_size, icon_size))  # Spacing between buttons
        self.icon3_button.setIcon(QIcon("wprevious.png"))  # Set your third icon here
        self.icon3_button.setIconSize(QSize(20, 20))
        self.icon3_button.setStyleSheet("background-color: transparent; border: none;")
        self.icon3_button.clicked.connect(play_next)  # Connect to a function

        # self.play_pause_button = QPushButton("Play/Pause", self)
        # self.next_button = QPushButton("Next", self)
        # self.previous_button = QPushButton("Previous", self)
        #
        # self.play_pause_button.setGeometry(QRect(15, 160, 100, 30))
        # self.next_button.setGeometry(QRect(120, 160, 100, 30))
        # self.previous_button.setGeometry(QRect(225, 160, 100, 30))
        #
        # # Set styles for buttons
        # self.play_pause_button.setStyleSheet("background-color: #1DB954; color: white;")
        # self.next_button.setStyleSheet("background-color: #1DB954; color: white;")
        # self.previous_button.setStyleSheet("background-color: #1DB954; color: white;")
        #
        # # Connect buttons to slots
        # # self.play_pause_button.clicked.connect(self.pause_playback)
        # self.next_button.clicked.connect(self.play_next)
        # self.previous_button.clicked.connect(self.play_previous)
        # Check if Spotify is running

        self.process_check_timer = QTimer(self)
        self.process_check_timer.timeout.connect(lambda: self.checkIfProcessRunning('spotify'))
        self.process_check_timer.start(1000)  # Call every 1 second
        self.checkIfProcessRunning('spotify')
        self.checkIfProcessRunning('discord')



    def toggle_playback(self):
        if self.is_playing:
            pause_playback()  # Call pause function
            self.is_playing = False  # Update the state to indicate it's paused
            self.icon1_button.setIcon(QIcon("wplay.png"))  # Optionally change the icon
        else:
            resume_playback()  # Call resume function
            self.is_playing = True  # Update the state to indicate it's playing
            self.icon1_button.setIcon(QIcon("wplay.png"))  # Optionally change the icon

    def showTime(self):
        current_time = QTime.currentTime()
        label_time = current_time.toString('hh:mm')
        self.label.setText(label_time)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def set_stylesheet(self, radius):
        self.centralwidget.setStyleSheet(
            '''
            background: rgb(0, 0, 0);
            border-top-left-radius:{0}px;
            border-bottom-left-radius:{0}px;
            border-top-right-radius:{0}px;
            border-bottom-right-radius:{0}px;
            '''
        )

    def animate_size(self, size):
        animation = QPropertyAnimation(self, b"size")
        animation.setDuration(300)  # Animation duration in milliseconds
        animation.setEndValue(size)
        animation.start()

    def enterEvent(self, event):
        # Expand the toolbar to show the input box (command_app)
        self.centralwidget.setStyleSheet(
            '''
            background: rgb(0, 0, 0);
            border-top-left-radius:{0}px;
            border-bottom-left-radius:{0}px;
            border-top-right-radius:{0}px;
            border-bottom-right-radius:{0}px;
            '''.format(self.h / 2)
        )

        new_x = self.getCentered - (self.w1 - self.w) // 2
        self.setGeometry(new_x, 10, self.w1, self.h1)  # Adjust size to accommodate input area

        self.command_app.show()  # Show the input box
        self.output_area.hide()  # Hide the output area while hovering
        self.label.setGeometry(QRect(self.w1 - 80, 15, 60, 18))
        super().enterEvent(event)  # Ensure other event processing happens

    def leaveEvent(self, event):
        # Reset radius and resize when cursor leaves the widget
        self.set_stylesheet(self.h / 2)  # Reset radius to initial size
        self.animate_size(self.initial_size)

        # Reset to the original centered position
        self.setGeometry(self.getCentered, 10, self.w, self.h)
        self.label.setGeometry(QRect(345, 15, 300, 18))

        # Hide the command input box and output area when mouse leaves
        self.command_app.hide()
        self.output_area.hide()
        self.label.setGeometry(QRect(345, 15, 300, 18))
        super().leaveEvent(event)

    def checkIfProcessRunning(self, processName):
        process_icons = {
            'spotify': 'Spotify_Green.png',
            'discord': 'discord-mark-white.png',
            # Add more processes as needed
        }
        any_process_running = False

        # Starting position for icons
        x_position = 15
        y_position = 15
        icon_spacing = 25  # Adjust the spacing between icons as needed

        # Store the current icons to ensure they don't overlap
        current_icons = []

        for proc in psutil.process_iter(['name']):
            try:
                for process_name, icon in process_icons.items():
                    if process_name.lower() in proc.info['name'].lower():
                        any_process_running = True
                        label_name = f'{process_name}_label'

                        if label_name not in current_icons:
                            label = QLabel(self)
                            setattr(self, label_name, label)
                            pixmap = QPixmap(icon)
                            pixmap = pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                            getattr(self, label_name).setPixmap(pixmap)

                            # Set geometry for each icon
                            getattr(self, label_name).setGeometry(QRect(x_position, y_position, 18, 18))

                            # Add the label name to current icons
                            current_icons.append(label_name)

                            # Move x_position for the next icon
                            x_position += icon_spacing

                            getattr(self, label_name).show()

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        # if not process_running:
        #     for process_name, icon in process_icons.items():
        #         labell_name = f'{process_name}_label'
        #         if hasattr(self, 'labell_name'):
        #             self.spotify_label.hide()  # Hide the QLabel
        #             self.spotify_label.deleteLater()  # Properly delete the QLabel to avoid memory leaks
        #             del self.spotify_label  # Delete the reference to the QLabel
        #
        #     return False


# Updated CommandApp to handle UI expansion and display output
class CommandApp(QWidget):
    def __init__(self, output_widget=None, toolbar=None):
        super().__init__()
        self.init_ui()
        self.output_widget = output_widget  # Reference to the output area
        self.toolbar = toolbar  # Reference to the main toolbar for expansion

    def init_ui(self):
        # Set up a minimal layout with just the QLineEdit
        self.layout = QVBoxLayout()

        # Text input field (QLineEdit)
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter command...")
        self.text_input.returnPressed.connect(self.handle_command)  # Handle 'Enter' press

        # Add the input field to the layout
        self.layout.addWidget(self.text_input)

        # Set the layout to the QWidget
        self.setLayout(self.layout)

        # icons
        # self.iconss = QWidget(self)
        # self.iconss.setGeometry(345, 25, 300, 18)

        label = QLabel()

        pixmap = QPixmap("play_next.png")


        # Set the geometry of the QPixmap

        pixmap = pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        label.setPixmap(pixmap)

        label.setGeometry(345, 25, 300, 18)  # Set the geometry of the QLabel
        self.show()
        # Remove window borders and make it non-resizable
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Set the window size
        self.setFixedSize(400, 50)

        # Center the window on the screen
        self.move(500, 300)

        # Set the background color of the window and text color of the input field
        self.setStyleSheet("""
            background-color: black;
            color: white;
        """)

        # Set the text input field style separately to ensure white text
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: black;
                color: white;
                border: none;
            }
        """)
        # Show the window
        self.show()


    def handle_command(self):
        # Get the user input
        command = self.text_input.text().lower()

        if command:  # Only expand if input is provided
            # Expand the toolbar UI when Enter is pressed
            # self.toolbar.further_expand()

            # Command handling logic
            output = ""  # Placeholder for command output
            if command == "open youtube":
                output = "Opening YouTube..."
                open_yt()

            elif command == "youtube":
                output = "Searching YouTube..."
                yt()

            elif command == "transfer playlist":
                output = "Transferring playlist..."
                final()

            elif command == "open spotify":
                output = "Opening Spotify..."
                open_spotify()

            elif command == "download":
                output = "paste the link of the file you want to download..."
                linkk = input()
                download_file(linkk)

            elif command == "pause":
                output = "Pausing Spotify..."
                pause_playback()

            elif command == "resume":
                output = "Resuming Spotify..."
                resume_playback()

            elif command == "play next":
                output = "Playing next track..."
                play_next()

            else:
                model = genai.GenerativeModel('gemini-pro')
                # chat = model.start_chat(history=[])
                chat = model.start_chat(history=[])
                input_text = self.text_input.text()  # Get the input from the text field
                chat.send_message(input_text)  # Send the input to the chat
                latest_message = chat.history[-1]
                response_text = latest_message.parts[0].text
                # cleaned_response = self.clean_text(response_text)  # Assuming clean_text is a method in your class
                # output = f"AI: {cleaned_response}"
                output = f"AI: {response_text}"


            # Display output in the output area

            self.toolbar.output_area.setText(output)  # Show command output in the QTextEdit
            self.toolbar.output_area.show()  # Ensure the output area is visible

            # Clear the input field after submission
            self.text_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToolBar()
    window.show()
    sys.exit(app.exec_())