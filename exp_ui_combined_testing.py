from PyQt5.QtCore import *
from PyQt5.QtGui import *
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

class ToolBar(QWidget):
    def __init__(self):
        super(ToolBar, self).__init__()

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

        self.label = QLabel(self)
        self.label.setStyleSheet("background-color:transparent;color: #FFFFFF;font-family: 'Arial'; font-size: 14px; font-weight: bold; padding: 0;")
        self.label.setGeometry(QRect(345, 15, 300, 18))

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)  # Update every second

        # Add CommandApp widget (the input box) below Spotify icon
        self.command_app = CommandApp(output_widget=None, toolbar=self)  # Pass toolbar reference for expansion
        self.command_app.setParent(self)
        self.command_app.setGeometry(QRect(15, 40, 350, 30))  # Position under the Spotify icon
        self.command_app.hide()  # Hide initially until enterEvent is triggered

        # Add QTextEdit widget (output area) below the input box
        self.output_area = QTextEdit(self)
        self.output_area.setGeometry(QRect(15, 80, 350, 80))  # Position below the input box
        self.output_area.setStyleSheet("background-color: black; color: white; border: none;")
        self.output_area.setReadOnly(True)  # Output area is not editable
        self.output_area.hide()  # Hide initially

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
        process_running = False

        # Iterate over all processes to check if the processName is running
        for proc in psutil.process_iter(['name']):
            try:
                if processName.lower() in proc.info['name'].lower():
                    process_running = True

                    # If the process is running and the QLabel doesn't exist, create it
                    if not hasattr(self, 'spotify_label'):
                        self.spotify_label = QLabel(self)
                        pixmap = QPixmap('Spotify_Green.png')
                        pixmap = pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Scale pixmap to fit QLabel
                        self.spotify_label.setGeometry(QRect(15, 15, 18, 18))  # Set the QLabel size
                        self.spotify_label.setPixmap(pixmap)
                        self.spotify_label.show()
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # If the process is not running, hide and delete the QLabel if it exists
        if not process_running:
            if hasattr(self, 'spotify_label'):
                self.spotify_label.hide()  # Hide the QLabel
                self.spotify_label.deleteLater()  # Properly delete the QLabel to avoid memory leaks
                del self.spotify_label  # Delete the reference to the QLabel

        return False


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
                output = f"Unrecognized command: {command}"

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