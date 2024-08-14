import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QSlider, QCheckBox, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import librosa
import librosa.display
import matplotlib.pyplot as plt
import audio_converter


class SpectrogramCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        super(SpectrogramCanvas, self).__init__(fig)
        self.setParent(parent)
        plt.tight_layout()


    def plot_spectrogram(self, audio_path):
        y, sr = librosa.load(audio_path, sr=None)
        S = librosa.stft(y)
        S_db = librosa.amplitude_to_db(abs(S))

        self.ax.clear()

        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz', ax=self.ax, cmap='magma')
        self.ax.set_title('Spectrogram')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Frequency (Hz)')
        
        self.ax.figure.colorbar(img, ax=self.ax, format='%+2.0f dB')
        self.draw()



class ImageToAudioConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.image_path = ""
        self.initUI()


    def initUI(self):
        layout = QVBoxLayout()
        self.resize(600, 800)

        # File selection
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        select_button = QPushButton("Select Image")
        select_button.clicked.connect(self.select_file)
        select_button.setMinimumSize(150, 70)
        select_button.setMaximumSize(1000, 100)
        layout.addWidget(select_button)

        # Sliders for frequency range
        layout.addWidget(QLabel("Bottom Frequency (Hz):"))
        self.bottom_freq_slider = QSlider(Qt.Horizontal)
        self.bottom_freq_slider.setRange(20, 20000)
        self.bottom_freq_slider.setValue(200)
        self.bottom_freq_slider.valueChanged.connect(self.update_bottom_freq_label)
        bottom_freq_layout = QHBoxLayout()
        bottom_freq_layout.addWidget(self.bottom_freq_slider)
        self.bottom_freq_label = QLabel("200")
        bottom_freq_layout.addWidget(self.bottom_freq_label)
        layout.addLayout(bottom_freq_layout)

        layout.addWidget(QLabel("Top Frequency (Hz):"))
        self.top_freq_slider = QSlider(Qt.Horizontal)
        self.top_freq_slider.setRange(20, 20000)
        self.top_freq_slider.setValue(20000)
        self.top_freq_slider.valueChanged.connect(self.update_top_freq_label)
        top_freq_layout = QHBoxLayout()
        top_freq_layout.addWidget(self.top_freq_slider)
        self.top_freq_label = QLabel("20000")
        top_freq_layout.addWidget(self.top_freq_label)
        layout.addLayout(top_freq_layout)

        # Slider for pixels per second
        layout.addWidget(QLabel("Pixels per Second:"))
        self.pixels_slider = QSlider(Qt.Horizontal)
        self.pixels_slider.setRange(1, 100)
        self.pixels_slider.setValue(30)
        self.pixels_slider.valueChanged.connect(self.update_pixels_label)
        pixels_layout = QHBoxLayout()
        pixels_layout.addWidget(self.pixels_slider)
        self.pixels_label = QLabel("30")
        pixels_layout.addWidget(self.pixels_label)
        layout.addLayout(pixels_layout)

        # Slider for sampling rate
        layout.addWidget(QLabel("Sampling Rate:"))
        self.sampling_rate_slider = QSlider(Qt.Horizontal)
        self.sampling_rate_slider.setRange(8000, 96000)
        self.sampling_rate_slider.setValue(44100)
        self.sampling_rate_slider.valueChanged.connect(self.update_sampling_rate_label)
        sampling_rate_layout = QHBoxLayout()
        sampling_rate_layout.addWidget(self.sampling_rate_slider)
        self.sampling_rate_label = QLabel("44100")
        sampling_rate_layout.addWidget(self.sampling_rate_label)
        layout.addLayout(sampling_rate_layout)

        # Rotate and Invert checkboxes
        self.rotate_checkbox = QCheckBox("Rotate 90°")
        layout.addWidget(self.rotate_checkbox)

        self.invert_checkbox = QCheckBox("Invert Colors")
        layout.addWidget(self.invert_checkbox)

        # Convert button
        convert_button = QPushButton("Convert to Audio")
        convert_button.clicked.connect(self.convert_to_audio)
        convert_button.setMinimumSize(100, 20)
        convert_button.setMaximumSize(1000, 30)
        layout.addWidget(convert_button)

        self.spectrogram_canvas = SpectrogramCanvas(self)
        layout.addWidget(self.spectrogram_canvas)

        self.setLayout(layout)
        self.setWindowTitle('Image to Audio Converter')


    def update_bottom_freq_label(self, value):
        self.bottom_freq_label.setText(str(value))

    def update_top_freq_label(self, value):
        self.top_freq_label.setText(str(value))

    def update_pixels_label(self, value):
        self.pixels_label.setText(str(value))

    def update_sampling_rate_label(self, value):
        self.sampling_rate_label.setText(str(value))

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

        start_time = time.time()

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

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.2f} seconds")


        self.spectrogram_canvas.plot_spectrogram(output_path)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageToAudioConverter()
    ex.show()
    sys.exit(app.exec_())
