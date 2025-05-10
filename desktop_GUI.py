import sys
import requests
import json
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QSlider, QComboBox,
    QLineEdit, QCheckBox, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from TTS import KrutrimTTS
from new_maps import route_details
from location_suggestions import get_location_suggestions, geo_loc


class HelmetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OLA Smart Helmet KAVACH")
        self.setWindowIcon(QIcon('helmet_icon.png'))  # Add an icon file
        self.setGeometry(100, 100, 900, 700)

        # Initialize UI
        self.init_ui()

        # Initialize flags and state
        self.busy_flag = 1
        self.status_flag = 1
        self.send_flags_active = True
        self.route_data = None

        # Set up timer for continuous flag sending
        self.flag_timer = QTimer()
        self.flag_timer.timeout.connect(self.send_flags_to_esp)
        self.flag_timer.start(1000)  # Every 1 second

        # Initialize TTS
        self.tts = KrutrimTTS("uxoTDYB_nRDizByWW0t91BE-7")

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Set style
        self.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QLabel {
                font-size: 13px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        # Add sections to the main layout
        self.create_configuration_section(main_layout)
        self.create_route_section(main_layout)
        self.create_communication_section(main_layout)

        # Status bar
        self.statusBar().showMessage("Ready")

    def create_configuration_section(self, parent_layout):
        # Configuration Section
        config_group = QGroupBox("⚙️ Helmet Configuration")
        parent_layout.addWidget(config_group)

        layout = QVBoxLayout()
        config_group.setLayout(layout)

        # First row of toggles
        row1 = QHBoxLayout()
        self.voice_assist = QCheckBox("Voice Guidance")
        self.voice_assist.setChecked(True)
        row1.addWidget(self.voice_assist)

        self.auto_indicator = QCheckBox("Auto Turn Signals")
        self.auto_indicator.setChecked(True)
        row1.addWidget(self.auto_indicator)

        self.vehicle_control = QCheckBox("Vehicle Controls")
        self.vehicle_control.setChecked(True)
        row1.addWidget(self.vehicle_control)
        layout.addLayout(row1)

        # Second row of toggles
        row2 = QHBoxLayout()
        self.hazard_light = QCheckBox("Auto Hazard Lights")
        row2.addWidget(self.hazard_light)

        self.phone_connect = QCheckBox("Phone Connectivity")
        self.phone_connect.setChecked(True)
        row2.addWidget(self.phone_connect)
        layout.addLayout(row2)

        # Sliders
        self.audio_speed = self.create_slider("Audio Speed", 0, 10, 5, layout)
        self.audio_tone = self.create_slider("Audio Tone", 0, 10, 5, layout)
        self.volume = self.create_slider("Volume Level", 0, 10, 5, layout)

        # Advanced Settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout()
        advanced_group.setLayout(advanced_layout)

        self.esp_ip = QLineEdit("192.168.232.190")
        self.esp_port = QLineEdit("80")

        advanced_layout.addWidget(QLabel("ESP32 IP Address:"))
        advanced_layout.addWidget(self.esp_ip)
        advanced_layout.addWidget(QLabel("Port:"))
        advanced_layout.addWidget(self.esp_port)

        layout.addWidget(advanced_group)

        # Animation Selection
        self.animation_select = QComboBox()
        self.animation_select.addItems([
            "Wipe left to right",
            "Wipe Right to Left",
            "Blink All",
            "Bounce (Knight Rider)",
            "Moving Dot",
            "Breathing"
        ])
        layout.addWidget(QLabel("Select Animation:"))
        layout.addWidget(self.animation_select)

    def create_slider(self, label, min_val, max_val, default, parent_layout):
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(QLabel(label))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider_layout.addWidget(slider)
        parent_layout.addLayout(slider_layout)
        return slider

    def create_route_section(self, parent_layout):
        # Route Planning Section
        route_group = QGroupBox("📍 Route Planning")
        parent_layout.addWidget(route_group)

        layout = QVBoxLayout()
        route_group.setLayout(layout)

        # Origin and Destination
        self.origin_input = QLineEdit()
        self.dest_input = QLineEdit()

        layout.addWidget(QLabel("Enter starting point:"))
        layout.addWidget(self.origin_input)
        layout.addWidget(QLabel("Enter destination:"))
        layout.addWidget(self.dest_input)

        # Suggestions
        self.origin_suggestions = QComboBox()
        self.dest_suggestions = QComboBox()

        self.origin_input.textChanged.connect(
            lambda: self.update_suggestions(self.origin_input, self.origin_suggestions))
        self.dest_input.textChanged.connect(lambda: self.update_suggestions(self.dest_input, self.dest_suggestions))

        layout.addWidget(QLabel("Origin suggestions:"))
        layout.addWidget(self.origin_suggestions)
        layout.addWidget(QLabel("Destination suggestions:"))
        layout.addWidget(self.dest_suggestions)

        # Calculate Route Button
        self.calc_route_btn = QPushButton("Calculate Route")
        self.calc_route_btn.clicked.connect(self.calculate_route)
        layout.addWidget(self.calc_route_btn)

        # Route Details
        self.route_details = QTextEdit()
        self.route_details.setReadOnly(True)
        layout.addWidget(self.route_details)

    def create_communication_section(self, parent_layout):
        # Communication Section
        comm_group = QGroupBox("📲 Helmet Communication")
        parent_layout.addWidget(comm_group)

        layout = QVBoxLayout()
        comm_group.setLayout(layout)

        # Send Configuration Button
        self.send_config_btn = QPushButton("Send Configuration to Helmet")
        self.send_config_btn.clicked.connect(self.send_configuration)
        layout.addWidget(self.send_config_btn)

        # Status Label
        self.comm_status = QLabel("Ready")
        layout.addWidget(self.comm_status)

    def update_suggestions(self, input_field, combo_box):
        text = input_field.text()
        if len(text) > 2:
            try:
                suggestions = get_location_suggestions(text)
                combo_box.clear()
                combo_box.addItems(suggestions)
            except Exception as e:
                print(f"Error getting suggestions: {e}")

    def calculate_route(self):
        origin = self.origin_suggestions.currentText() or self.origin_input.text()
        destination = self.dest_suggestions.currentText() or self.dest_input.text()

        if not origin or not destination:
            QMessageBox.warning(self, "Input Error", "Please enter both origin and destination")
            return

        self.route_details.setPlainText("Calculating route...")
        self.calc_route_btn.setEnabled(False)

        # Run in a separate thread to avoid UI freeze
        def calculate():
            try:
                origin_coords = geo_loc(origin)
                dest_coords = geo_loc(destination)

                if None in origin_coords or None in dest_coords:
                    self.show_message("Error", "Could not get coordinates for the locations")
                    return

                distance, duration, instr1, instr2, inst1_dist, inst2_dist = route_details(origin_coords, dest_coords)

                self.route_data = {
                    'distance': distance,
                    'duration': duration,
                    'instructions': [instr1, instr2],
                    'coords': {
                        'origin': origin_coords,
                        'destination': dest_coords
                    },
                    'Instruction_dist': [inst1_dist, inst2_dist]
                }

                result_text = (
                    f"Route from {origin} to {destination}\n"
                    f"Distance: {distance}\n"
                    f"Duration: {duration}\n\n"
                    f"Directions:\n"
                    f"1. {instr1} ({inst1_dist}m)\n"
                    f"2. {instr2} ({inst2_dist}m)"
                )

                self.route_details.setPlainText(result_text)
                self.show_message("Success", "Route calculated successfully!")

            except Exception as e:
                self.show_message("Error", f"Route calculation failed: {str(e)}")
            finally:
                self.calc_route_btn.setEnabled(True)

        # Start the calculation thread
        threading.Thread(target=calculate, daemon=True).start()

    def send_configuration(self):
        if not self.esp_ip.text() or not self.esp_port.text():
            self.show_message("Error", "Please enter ESP32 IP and Port")
            return

        # Prepare payload
        payload = {
            'voice_assist': int(self.voice_assist.isChecked()),
            'auto_indicator': int(self.auto_indicator.isChecked()),
            'hazard_light': int(self.hazard_light.isChecked()),
            'connect_phone': int(self.phone_connect.isChecked()),
            'vehicle_control': int(self.vehicle_control.isChecked()),
            'volume': self.volume.value(),
            'audio_speed': self.audio_speed.value(),
            'audio_tone': self.audio_tone.value(),
            'animation': self.animation_select.currentIndex() + 1,
            'esp_ip': self.esp_ip.text(),
            'esp_port': self.esp_port.text()
        }

        # Add route data if available
        if self.route_data:
            def map_instr(instr):
                instr = instr.lower()
                if "left" in instr:
                    return 1 if "slight" not in instr else 6
                elif "right" in instr:
                    return 2 if "slight" not in instr else 5
                elif "straight" in instr or any(d in instr for d in ["north", "south", "east", "west"]):
                    return 3
                elif "uturn" in instr:
                    return 4
                return 0

            payload.update({
                'direction1_bit': map_instr(self.route_data['instructions'][0]),
                'direction2_bit': map_instr(self.route_data['instructions'][1]),
                'origin': self.origin_input.text(),
                'destination': self.dest_input.text(),
                'duration': self.route_data['duration'],
                'distance': self.route_data['distance'],
                'instruction_dist1': self.route_data['Instruction_dist'][0],
                'instruction_dist2': f"{self.route_data['instructions'][1]} {self.route_data['Instruction_dist'][1]}m",
                'coords': self.route_data['coords']
            })

        self.comm_status.setText("Sending configuration...")

        # Run in a separate thread
        def send_config():
            try:
                response = requests.post(
                    f"http://{self.esp_ip.text()}:{self.esp_port.text()}/",
                    json=payload,
                    timeout=5
                )

                if response.status_code == 200:
                    self.show_message("Success", "Helmet configured successfully!")
                else:
                    self.show_message("Error", f"Helmet connection failed (Status: {response.status_code})")
            except Exception as e:
                self.show_message("Error", f"Connection error: {str(e)}")
            finally:
                self.comm_status.setText("Ready")

        threading.Thread(target=send_config, daemon=True).start()

    def send_flags_to_esp(self):
        if not self.send_flags_active:
            return

        flags = {
            'Busy_flag': self.busy_flag,
            'Status_flag': self.status_flag
        }

        try:
            response = requests.post(
                f"http://{self.esp_ip.text()}:{self.esp_port.text()}/speech",
                json=flags,
                timeout=1
            )

            if response.status_code != 200:
                print(f"Failed to send flags (Status: {response.status_code})")
        except Exception as e:
            print(f"Flag sending error: {str(e)}")

    def tts_function(self):
        self.busy_flag = 1
        self.status_flag = 1

        try:
            data_tts = self.get_esp32_data()
            print("Data received from ESP32:", data_tts)

            if data_tts:
                audio_url = self.tts.generate_speech(data_tts)
                print("Audio URL:", audio_url)

                if audio_url:
                    print("Audio generation complete, now playing...")
                    if self.tts.download_and_play(audio_url):
                        # Audio played successfully
                        self.busy_flag = 0
                        self.status_flag = 0
                        print("Audio played successfully. Flags updated.")
                    else:
                        print("Failed to play audio. Flags remain set.")
                else:
                    print("Failed to generate audio. Flags remain set.")
            else:
                print("No data received from ESP32. Flags remain set.")
        except Exception as e:
            print(f"Error in TTS_function: {str(e)}")

    def get_esp32_data(self):
        try:
            payload = {
                "Busy_flag": False,
                "Status_flag": True
            }

            response = requests.post(
                f"http://{self.esp_ip.text()}:{self.esp_port.text()}/speech",
                json=payload,
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                if "audio_input" in data:
                    return data["audio_input"]
        except Exception as e:
            print(f"Error getting ESP32 data: {e}")
        return None

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def closeEvent(self, event):
        # Clean up when window is closed
        self.send_flags_active = False
        self.flag_timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = HelmetApp()
    window.show()
    sys.exit(app.exec_())