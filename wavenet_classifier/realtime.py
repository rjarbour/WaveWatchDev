import pyaudio
import numpy as np
import time
import keras.models as kmodels
import pprint
import threading
import copy

p = pyaudio.PyAudio()
c = threading.Condition()
CHUNK = 2**14
CHANNELS = 1
RATE = 9600
LEN = 1000
flag = 0
mx = kmodels.load_model("saved_wavenet_classifier_diffmax_4.h5")
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
player = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True, frames_per_buffer=CHUNK)
stream.start_stream()

np.set_printoptions(precision=2, suppress=True)

print("force memory initialization")
n = np.zeros(19200, dtype=np.int16)
n = np.reshape(n, (1, n.shape[0],))
mx.predict(n)

class Audio_t(threading.Thread):
    def __init__(self, name: object):
        threading.Thread.__init__(self)
        self.name = name
        self.last = time.time()

    def run(self):
        global flag
        global n
        global stream
        global player
        global c
        while True:
            data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
            c.acquire()
            n[0] = np.append(n[0][CHUNK:], data)
            c.notify_all()
            c.release()




class Predict_t(threading.Thread):
    def __init__(self, name: object):
        threading.Thread.__init__(self)
        self.name = name
        self.buff = np.array([])
        self.cl = ['door_wood_knock', 'clock_alarm', 'car_horn', 'siren', 'glass_breaking']

    def run(self):
        global flag
        global n
        global mx
        global c
        global player
        while True:
            c.acquire()
            self.buff = copy.deepcopy(n)
            c.notify_all()
            c.release()
            self.buff = np.diff(self.buff)
            self.buff = np.append(self.buff, [0.0])
            self.buff = (self.buff - self.buff.mean()) / self.buff.max()
            self.buff = self.buff.reshape(1, self.buff.shape[0])
            activations = mx.predict(self.buff)
            u = activations[0]
            scale_factor = np.ptp(u)
            b = (u - np.min(u)) / np.ptp(u)
            if max(b) != b[-1]:
                detect, val = self.cl[np.argmax(b)], np.argmax(b)
                print(detect, b, scale_factor)
            time.sleep(2)




"""
for i in range(int(LEN*RATE/CHUNK)): #go for a LEN seconds
    data = np.fromstring(stream.read(CHUNK),dtype=np.uint8)
    player.write(data,CHUNK)
    n[0] = np.append(n[0][512:], data)
    activations = mx.predict(n)
    u = activations[0]
    b = (u - np.min(u)) / np.ptp(u)
    c = ['door_wood_knock', 'clock_alarm', 'car_horn', 'siren', 'glass_breaking']
    if max(b) != b[-1]:
        detect, val = c[np.argmax(b)], np.argmax(b)
        print(detect, b)
"""

t1 = Audio_t("audio_t")
t2 = Predict_t("Predict_t")

t1.start()
t2.start()

while True:
    pass

stream.stop_stream()
stream.close()
p.terminate()