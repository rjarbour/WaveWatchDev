from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
import datetime

from kivy.config import Config

Builder.load_file('parenttest.kv')

class ParentTest(FloatLayout):
    pass


class MyTestApp(App):
    def build(self):
        pt = ParentTest()
        return pt



if __name__ == '__main__':
    MyTestApp().run()