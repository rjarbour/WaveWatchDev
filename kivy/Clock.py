from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
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

    def __init__(self, **kwargs):
        super(Ticks, self).__init__(**kwargs)
        self.bind(pos=self.update_clock)
        self.bind(size=self.update_clock)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
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

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        print("key")
        if keycode[1] == 'w':
            p = CustomPopup(self.on_popup_dismiss, self.dismiss_check)
            self.notification_stack.append(p)
            p.title = "notification {0}".format(len(self.notification_stack))
            if len(self.notification_stack) > 1:
                self.internal_dismiss = True
                self.notification_stack[-2].dismiss()
                self.internal_dismiss = False
            p.open()

    def dismiss_check(self):
        return self.internal_dismiss

    def on_popup_dismiss(self):
        print("dismissed")
        p = self.notification_stack.pop()
        del p
        if len(self.notification_stack) > 0:
            self.notification_stack[-1].open()
        pass

class MyClockApp(App):
    def build(self):
        clock = ClockApp()
        Clock.schedule_interval(clock.ticks.update_clock, 1.0 / 20)
        return clock



if __name__ == '__main__':
    MyClockApp().run()
