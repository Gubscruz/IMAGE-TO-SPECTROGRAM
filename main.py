import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QSlider, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt
import audio_converter


class ImageToAudioConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.image_path = ""
        self.initUI()


    def initUI(self):
        layout = QVBoxLayout()

        # File selection
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        select_button = QPushButton("Select Image")
        select_button.clicked.connect(self.select_file)
        select_button.setMinimumSize(150, 70)  # Minimum size
        select_button.setMaximumSize(500, 100)
        layout.addWidget(select_button)

        # Sliders for frequency range
        self.bottom_freq_slider = QSlider(Qt.Horizontal, )
        self.bottom_freq_slider.setRange(20, 20000)
        self.bottom_freq_slider.setValue(200)
        layout.addWidget(QLabel("Bottom Frequency (Hz):"))
        layout.addWidget(self.bottom_freq_slider)

        self.top_freq_slider = QSlider(Qt.Horizontal)
        self.top_freq_slider.setRange(20, 20000)
        self.top_freq_slider.setValue(20000)
        layout.addWidget(QLabel("Top Frequency (Hz):"))
        layout.addWidget(self.top_freq_slider)

        # Slider for pixels per second
        self.pixels_slider = QSlider(Qt.Horizontal)
        self.pixels_slider.setRange(1, 100)
        self.pixels_slider.setValue(30)
        layout.addWidget(QLabel("Pixels per Second:"))
        layout.addWidget(self.pixels_slider)

        # Slider for sampling rate
        self.sampling_rate_slider = QSlider(Qt.Horizontal)
        self.sampling_rate_slider.setRange(8000, 96000)
        self.sampling_rate_slider.setValue(44100)
        layout.addWidget(QLabel("Sampling Rate:"))
        layout.addWidget(self.sampling_rate_slider)

        # Rotate and Invert checkboxes
        self.rotate_checkbox = QCheckBox("Rotate 90°")
        layout.addWidget(self.rotate_checkbox)

        self.invert_checkbox = QCheckBox("Invert Colors")
        layout.addWidget(self.invert_checkbox)

        # Convert button
        convert_button = QPushButton("Convert to Audio")
        convert_button.clicked.connect(self.convert_to_audio)
        layout.addWidget(convert_button)

        self.setLayout(layout)
        self.setWindowTitle('Image to Audio Converter')


    def select_file(self):
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if self.image_path:
            self.file_label.setText(self.image_path.split("/")[-1])


    def convert_to_audio(self):
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Please select an image file.")
            return

        output_path, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "", "WAV Files (*.wav)")
        if not output_path:
            return

        audio_converter.convert_image_to_audio(
            self.image_path,
            output_path,
            minfreq=self.bottom_freq_slider.value(),
            maxfreq=self.top_freq_slider.value(),
            pxs=self.pixels_slider.value(),
            wavrate=self.sampling_rate_slider.value(),
            rotate=self.rotate_checkbox.isChecked(),
            invert=self.invert_checkbox.isChecked()
        )
        QMessageBox.information(self, "Success", f"Audio file has been saved to {output_path}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageToAudioConverter()
    ex.show()
    sys.exit(app.exec_())
