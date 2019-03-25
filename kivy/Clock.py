from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
import datetime

from kivy.config import Config

Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '200')

Builder.load_file('clock.kv')


class ClockApp(FloatLayout):
    pass

class CustomPopup(Popup):
    pass


class Ticks(Widget):
    my_list_prop = ListProperty()

    def __init__(self, **kwargs):
        super(Ticks, self).__init__(**kwargs)
        self.bind(pos=self.update_clock)
        self.bind(size=self.update_clock)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

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

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        print("key")
        if keycode[1] == 'w':
            p = CustomPopup()
            p.open()

class MyClockApp(App):
    def build(self):
        clock = ClockApp()
        Clock.schedule_interval(clock.ticks.update_clock, 1.0 / 20)
        return clock



if __name__ == '__main__':
    MyClockApp().run()
