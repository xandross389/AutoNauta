from kivy.core.window import Window
from kivy.app import App
from main_window import MainWindow


class AutoNautaApp(App):
    Window.minimum_height = 540
    Window.minimum_width = 700

    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.stop.set()

    def build(self):
        return MainWindow()
