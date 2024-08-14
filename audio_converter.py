import cv2
import wave
import math
import array

def convert_image_to_audio(image_path, output, minfreq=200, maxfreq=20000, pxs=30, wavrate=44100, rotate=False, invert=False):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if rotate:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    if invert:
        image = cv2.bitwise_not(image)

    output_wave = wave.open(output, 'w')
    output_wave.setparams((1, 2, wavrate, 0, 'NONE', 'not compressed'))

    freqrange = maxfreq - minfreq
    interval = freqrange / image.shape[0]

    fpx = wavrate // pxs
    data = array.array('h')

    for x in range(image.shape[1]):
        row = []
        for y in range(image.shape[0]):
            yinv = image.shape[0] - y - 1
            amp = image[y, x]
            if amp > 0:
                row.append(genwave(yinv * interval + minfreq, amp, fpx, wavrate))

        for i in range(fpx):
            for j in row:
                try:
                    data[i + x * fpx] += j[i]
                except(IndexError):
                    data.insert(i + x * fpx, j[i])
                except(OverflowError):
                    if j[i] > 0:
                        data[i + x * fpx] = 32767
                    else:
                        data[i + x * fpx] = -32768

    output_wave.writeframes(data.tobytes())
    output_wave.close()

def genwave(frequency, amplitude, samples, samplerate):
    cycles = samples * frequency / samplerate
    a = []
    for i in range(samples):
        x = math.sin(float(cycles) * 2 * math.pi * i / float(samples)) * float(amplitude)
        a.append(int(math.floor(x)))
    return a
