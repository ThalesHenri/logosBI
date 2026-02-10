#configurações da janela principal
import dearpygui.dearpygui as dpg
from .callbacks import Callbacks

class MainWindow:
    def __init__(self,label:str,tag:str)-> None:
        self.label = label
        self.tag = tag
        
        self.build()
        
        
        
    def build(self)-> None:
        with dpg.window(
            label=self.label, 
            no_title_bar=True,
            no_move=True,
            no_collapse=True, 
            tag=self.tag):
            self._header()
            self._pedido_info()
            self._itens_table()
            self._totais()
        dpg.set_primary_window(self.tag, True)
    
    
    def _header(self):
        dpg.add_text("Bem-vindo ao LogosBI - Analisador de Pedidos",tag="header")
        dpg.add_spacer(height=20)
        dpg.add_text("Este sistema foi desenvolvido por TH Sistemase tem a finalidade de extrair, analisar e visualizar informações de pedidos em formato PDF, facilitando a gestão e tomada de decisões para empresas do varejo.")
        dpg.add_text("Abaixo estão suas ações disponíveis:")
        dpg.add_separator()
        dpg.add_button(label="Importar PDF",tag="btn_importar_pdf",callback=Callbacks.importar_pdf)
        dpg.add_button(label="Dados Gerados",tag="btn_dados_gerados")


    def _pedido_info(self):
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_text("Número do Pedido:")
            dpg.add_text("-",tag="pedido_numero")
            dpg.add_spacer(width=20)
            dpg.add_text("Data da Venda:")
            dpg.add_text("-",tag="pedido_data")
            
    
    
    def _itens_table(self):
        dpg.add_spacer()
        dpg.add_text("Itens do Pedido")
        dpg.add_separator()

        with dpg.table(
            tag="itens_table",
            header_row=True,
            resizable=True,
            borders_innerH=True,
            borders_outerH=True
        ):
            dpg.add_table_column(label="Código")
            dpg.add_table_column(label="Descrição")
            dpg.add_table_column(label="Qtd")
            dpg.add_table_column(label="Unitário")
            dpg.add_table_column(label="Total")
    
    
    def _totais(self):
        dpg.add_spacer(height=20)
        dpg.add_text("Total s/ Impostos: R$ 0,00", tag="total_sem_impostos")
        dpg.add_text("Total Final: R$ 0,00", tag="total_final")
        