import cv2
import wave
import math
import numpy as np

def resize_image_if_needed(image, max_width=500, max_height=500):
    """
    Redimensiona a imagem para que sua largura ou altura não excedam os limites máximos,
    mantendo a proporção.
    """
    height, width = image.shape[:2]

    if width > max_width or height > max_height:
        scaling_factor = min(max_width / width, max_height / height)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    
    return image



def convert_image_to_audio(image_path, output, minfreq, maxfreq, pxs, wavrate, rotate, invert):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)    
    image = resize_image_if_needed(image)
    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)


    if rotate:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    if invert:
        image = cv2.bitwise_not(image)

    output_wave = wave.open(output, 'w')
    output_wave.setparams((1, 2, wavrate, 0, 'NONE', 'not compressed'))

    freq_range = maxfreq - minfreq
    interval = freq_range / image.shape[0]

    # Pre-allocate the audio data array for efficiency
    total_samples = image.shape[1] * (wavrate // pxs)
    data = np.zeros(total_samples, dtype=np.int16)

    # Step 4: Vectorized generation of sine waves for each column of pixels
    fpx = wavrate // pxs

    for x in range(image.shape[1]):
        freqs = minfreq + (np.arange(image.shape[0])[::-1] * interval)  # Vectorized frequency calculation
        amps = image[:, x]  # Amplitudes (pixel values)

        for y, (freq, amp) in enumerate(zip(freqs, amps)):
            if amp > 0:
                sine_wave = genwave(freq, amp, fpx, wavrate)
                data[x * fpx:x * fpx + fpx] += sine_wave


    data = np.clip(data, -32768, 32767)
    output_wave.writeframes(data.tobytes())
    output_wave.close()


def genwave(frequency, amplitude, samples, samplerate):
    t = np.arange(samples)
    wave = np.sin(2 * np.pi * frequency * t / samplerate) * amplitude
    return wave.astype(np.int16)
