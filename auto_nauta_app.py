from kivy.core.window import Window
from kivy.app import App
from main_window import MainWindow


class AutoNautaApp(App):
    Window.minimum_height = 540
    Window.minimum_width = 700

    def build(self):
        return MainWindow()
