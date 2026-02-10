import dearpygui.dearpygui as dpg
from .state import AppState
from etl import PedidoPDFExtractor
from config import PATH_INPUT
import os
from logger import LoggerMaker
from etl.pipeline import PedidoPipeline

logger = LoggerMaker().get_logger()
class Callbacks:
    
    @staticmethod
    def importar_pdf(sender, app_data, user_data)->None:
        #aqui deve abrir um dialogo para escolher o arquivo, e depois chamar o extractor
        logger.info("Iniciando a pipeline de importação de PDF")
        #pipeline aqui: varrer a input, pegar o primeiro pdf, extrair os dados, comparar com o banco, atualizar o banco de dados,informar o sucesso ou falha da operação, atualizar a tela)
        try:
            repository = AppState.repository
        except Exception as e:
            logger.error(f"Erro ao acessar o repositório: {e}")
            return
        repository.connect()
        pipeline = PedidoPipeline(repository)
        pipeline.varrer_input()
            
        #atualizar o estado da aplicação com os dados extraídos
        #reminder: Implementar depois
        
        
    @staticmethod
    def atualizar_tela()->None:
        pedido = AppState.pedido
        if not pedido:
            return dpg.set_value("pedido_numero", "-"), dpg.set_value("pedido_data", "-"), dpg.set_value("total_sem_impostos", "Total s/ Impostos: R$ 0,00"), dpg.set_value("total_final", "Total Final: R$ 0,00")
            
        dpg.set_value("pedido_numero", pedido["numero_pedido"])
        dpg.set_value("pedido_data", pedido["data_venda"])
        
        dpg.set_value("total_sem_impostos", f'Total s/ Impostos: R$ {pedido["total_sem_impostos"]}')
        dpg.set_value("total_final", f'Total Final: R$ {pedido["total_final"]}') 

