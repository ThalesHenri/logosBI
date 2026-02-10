# orquestrador da UI
import dearpygui.dearpygui as dpg
from .main_window import MainWindow
from .callbacks import Callbacks

class LogosBIApp:
    def __init__(self):
        dpg.create_context()
        self.main_window = MainWindow(label="LogosBI - Analisador de Pedidos", tag="main_window")
        self._setup_callbacks()
        
    def _setup_callbacks(self):
        dpg.set_item_callback("btn_importar_pdf", Callbacks.importar_pdf)
        
    def run(self):
        dpg.create_viewport(
            title='LogosBI - Analisador de Pedidos', 
            width=800, 
            height=600,
            resizable=True,
            decorated=True
            )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.maximize_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()