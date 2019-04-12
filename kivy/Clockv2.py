from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
import datetime
import pyaudio
import numpy as np
import time
import keras.models as kmodels
import pprint
import threading
import copy

from kivy.config import Config

Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '200')

Builder.load_file('clock.kv')


class ClockApp(FloatLayout):
    pass

class CustomPopup(Popup):

    def __init__(self, dismiss_callback, dismiss_check):
        super().__init__()
        self.d_callback = dismiss_callback
        self.d_check = dismiss_check

    def on_dismiss(self):
        if not self.d_check():
            self.d_callback()
        pass


class Ticks(Widget):
    notification_stack = ListProperty()
    internal_dismiss = BooleanProperty()
    detection_str = StringProperty()

    def __init__(self, **kwargs):
        super(Ticks, self).__init__(**kwargs)
        self.bind(pos=self.update_clock)
        self.bind(size=self.update_clock)
        self.internal_dismiss = False

    def update_clock(self, *args):
        self.canvas.clear()
        with self.canvas:
            time = datetime.datetime.now()
            Color(0.1, 0.3, 0.1)
            Line(points=[self.center_x, self.center_y, self.center_x + 0.85 * self.r * sin(pi / 30 * time.second),
                         self.center_y + 0.8 * self.r * cos(pi / 30 * time.second)], width=1)
            Color(0.2, 0.5, 0.2)
            Line(points=[self.center_x, self.center_y, self.center_x + 0.7 * self.r * sin(pi / 30 * time.minute),
                         self.center_y + 0.7 * self.r * cos(pi / 30 * time.minute)], width=2, cap="round")
            Color(0.4, 0.7, 0.4)
            th = time.hour * 60 + time.minute
            Line(points=[self.center_x, self.center_y, self.center_x + 0.5 * self.r * sin(pi / 360 * th),
                         self.center_y + 0.5 * self.r * cos(pi / 360 * th)], width=2, cap="round")

            
    def dismiss_check(self):
        return self.internal_dismiss

    def on_popup_dismiss(self):
        print("dismissed")
        p = self.notification_stack.pop()
        del p
        if len(self.notification_stack) > 0:
            self.notification_stack[-1].open()
        pass

    def detect_check(self, *args):
        global str_detect
        if str_detect != "":
            self.detection_str = str_detect
            if len(self.notification_stack) > 0:
                if self.notification_stack[-1].detect != self.detection_str:
                    p = CustomPopup(self.on_popup_dismiss, self.dismiss_check)
                    p.detect = self.detection_str
                    self.notification_stack.append(p)
                    p.title = "{1} {0}".format(len(self.notification_stack), p.detect)
                    if len(self.notification_stack) > 1:
                        self.internal_dismiss = True
                        self.notification_stack[-2].dismiss()
                        self.internal_dismiss = False
                    p.open()
            else:
                p = CustomPopup(self.on_popup_dismiss, self.dismiss_check)
                p.detect = self.detection_str
                self.notification_stack.append(p)
                p.title = "{1} {0}".format(len(self.notification_stack), p.detect)
                if len(self.notification_stack) > 1:
                    self.internal_dismiss = True
                    self.notification_stack[-2].dismiss()
                    self.internal_dismiss = False
                p.open()
        str_detect = ""
        

class MyClockApp(App):
    def build(self):
        clock = ClockApp()
        Clock.schedule_interval(clock.ticks.update_clock, 1.0 / 20)
        Clock.schedule_interval(clock.ticks.detect_check, 1.0)
        return clock


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
        self.cl = ['door_wood_knock', 'clock_alarm', 'car_horn', 'siren', 'ambient']
        self.prev_det = ""

    def run(self):
        global flag
        global n
        global mx
        global c
        global player
        global str_detect
        while True:
            c.acquire()
            self.buff = copy.deepcopy(n)
            c.notify_all()
            c.release()
            if self.buff.max() <= 11000:
                time.sleep(1)
                continue
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
                if scale_factor >= 0.9 and detect == self.prev_det:
                    str_detect = detect
                    print("detection reported")
                self.prev_det = detect
            else:
                self.prev_det = ""
                    





if __name__ == '__main__':
    p = pyaudio.PyAudio()
    c = threading.Condition()
    CHUNK = 2**14
    CHANNELS = 1
    RATE = 9600
    LEN = 1000
    flag = 0
    str_detect = ""
    mx = kmodels.load_model("saved_wavenet_classifier_diffmax_4.h5")
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
    stream.start_stream()

    np.set_printoptions(precision=2, suppress=True)

    print("force memory initialization")
    n = np.zeros(19200, dtype=np.int16)
    n = np.reshape(n, (1, n.shape[0],))
    mx.predict(n)
    t1 = Audio_t("audio_t")
    t2 = Predict_t("Predict_t")

    t1.start()
    t2.start()
    MyClockApp().run()

    while True:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()