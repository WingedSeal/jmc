import os
# os.environ["KIVY_NO_CONSOLELOG"] = "1"  # noqa
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # noqa
import tkinter as tk
import traceback
import json
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from tkinter import filedialog
from kivy.base import Builder
from kivy.clock import Clock
from typing import Tuple
from pathlib import Path
from kivy.app import App
from sys import argv, exit

from config import set_configs

Builder.load_file((Path(__file__).parent/'main.kv').as_posix())
CONFIG_FILE_NAME = 'jmc_config.json'
CONFIG_FILE = Path(argv[0]).parent/CONFIG_FILE_NAME
DEFAULT_CONFIG = {
    'namespace': 'default_namespace',
    'description': 'Compiled by JMC(Made by WingedSeal)',
    'pack_format': 7,
    'target': (Path(argv[0]).parent/'main.jmc').resolve().as_posix(),
    'output': Path(argv[0]).parent.resolve().as_posix(),
    'debug_mode': False
}


class TargetButton(Button):
    @staticmethod
    def get_target_path():
        root = tk.Tk()
        root.withdraw()
        return(filedialog.askopenfilename(filetypes=[("JMC", "*.jmc")]))


class OutputButton(Button):
    @staticmethod
    def get_output_path():
        root = tk.Tk()
        root.withdraw()
        return(filedialog.askdirectory())


class Root(Widget):
    def __init__(self, configs, **kwargs) -> None:
        self.configs = configs
        super().__init__(**kwargs)

    def popup(self, title: str, text: str, close: bool = False) -> None:
        label = Label(text=text)
        label.texture_update()
        grid = GridLayout(cols=1, size_hint=(0.9, None),
                          height=label.texture_size[1]+40)
        grid.add_widget(label)
        scrollview = ScrollView()
        scrollview.add_widget(grid)
        end = Label(text='', size=(0, 0), size_hint=(0, 0))
        grid.add_widget(end)
        popup = Popup(title=title,
                      content=scrollview,
                      size_hint=(1, 0.8))
        scrollview.scroll_to(end)
        popup.open()
        if close:
            Clock.schedule_once(popup.dismiss, 3)

    def compile(self) -> None:
        try:
            set_configs(self.configs)
            from jmc import DataPack
            datapack = DataPack()
            datapack.init()
            datapack.compile()
            self.popup(
                "Success", f"\nSuccessfully compiled\n{self.configs['target']}\nto\n{self.configs['output']}", close=True)
        except FileNotFoundError as error:
            if self.configs['debug_mode']:
                self.popup(
                    f"Fail (Debug Mode)", f"{traceback.format_exc()}\nFileNotFoundError"
                )
            else:
                self.popup(
                    "Fail", f"File Missing\n{error}"
                )
        except BaseException as error:
            self.popup(
                f"Fail", f"{traceback.format_exc()}\nUnknown Error"
            )


class JMC(App):
    title = "JMC Compiler"
    icon = (Path(__file__).parent/'WingedSeal.ico').as_posix()

    def __init__(self, configs, start_popup: Tuple[str, str] = None, **kwargs):
        self.configs = configs
        self.start_popup = start_popup
        super().__init__(**kwargs)

    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        self.root = Root(self.configs)
        return self.root

    def on_start(self, **kwargs):
        if self.start_popup is not None:
            self.root.popup(
                text=self.start_popup[1], title=self.start_popup[0])

    def on_request_close(self, *args, **kwargs):
        with CONFIG_FILE.open('w+') as file:
            json.dump(self.root.configs, file, indent=2)


def main():
    popup_text = None
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open('r') as file:
                configs = DEFAULT_CONFIG | json.load(file)

        except json.JSONDecodeError:
            popup_text = (
                f"JSONDecodeError", f"Your {CONFIG_FILE_NAME} might have malformed JSON. \nAutomatically resetting the configs...")
            configs = DEFAULT_CONFIG
        except BaseException:
            popup_text = (
                f"Unknown Error", f"{traceback.format_exc()}\nResorting to default configurations."
            )
            configs = DEFAULT_CONFIG
    else:
        popup_text = (f"Configuration File Not Found",
                      f"{CONFIG_FILE_NAME} is not found.\nGenerating default configurations...\nFor documentation, https://wingedseal.github.io/docs.jmc/")
        configs = DEFAULT_CONFIG
    set_configs(configs)
    JMC(configs, popup_text).run()


if __name__ == '__main__':
    try:
        main()
    except BaseException as Exception:
        with (Path(argv[0]).parent/'jmc_error.log').open('w+') as file:
            file.write(
                f"Exception occured before GUI is able to open.\n\n{traceback.format_exc()}")
    exit()
