
from .state import AppState
from logger import LoggerMaker
from etl.pipeline import PedidoPipeline
import dearpygui.dearpygui as dpg



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
    def dados_gerados(sender, app_data, user_data)->None:
        # 1. Validação da Main Window
        main_window = user_data
        if main_window is None:
            logger.error("Erro: user_data (main_window) é nulo no callback dados_gerados.")
            return

        try:
            # 2. Uso do AppState de forma segura
            repository = AppState.repository
            repository.connect()  # Certifique-se de que o repositório está conectado antes de usar
            # Idealmente, o repositório já deve estar conectado ou gerenciar isso internamente
            
            # 3. Pipeline e busca de dados
            pipeline = PedidoPipeline(repository)
            pedidos = pipeline.listar_pedidos()
            
            # 4. Atualização da UI
            # Aqui é onde o DPG precisa de tags fixas para não dar erro -1
            if pedidos is not None:
                main_window.atualizar_tela_principal(pedidos)
                logger.info(f"Sucesso: {len(pedidos)} pedidos enviados para a UI.")
            else:
                logger.warning("Pipeline retornou lista de pedidos vazia.")
        
        except Exception as e:
            # O logger vai capturar o traceback real aqui
            logger.error(f"Erro fatal no callback: {e}", exc_info=True)
        
        
    @staticmethod
    def selecionar_pedido(sender, app_data, user_data)->None:
        main_window = user_data['main_window']
        pedido_id = user_data['pedido_id']
        
        try:
            repository = AppState.repository
            repository.connect()
            itens = repository.listar_itens_pedido(pedido_id)
            main_window.atualizar_tela_itens(itens)
        except:
            logger.error("Erro ao listar itens do pedido")
            
            
    @staticmethod
    def atualizar_dashboard(sender, app_data, user_data)->None:
        main_window = user_data['main_window']
        aba_ativa = user_data['aba_ativa']
    
        if aba_ativa == "tag_dashboard":
            try:
                pipeline = AppState.pipeline
                dados_kpi, dados_grafico = pipeline.gerar_dashboard_data()
                main_window.atualizar_dashboard_ui(dados_kpi, dados_grafico)
            except Exception as e:
                logger.error(f"Erro ao atualizar dashboard: {e}", exc_info=True)
        
        
    @staticmethod
    def faturamento_ajuda(sender, app_data, user_data)->None:
        main_window = user_data['main_window']
        titulo = "Ajuda: Tendência Diária de Faturamento"
        texto = """Este gráfico mostra a tendência do faturamento diário com base nos dados extraídos dos PDFs de pedidos.
        - O eixo X representa os dias (cada ponto corresponde a um dia específico).
        - O eixo Y representa o faturamento diário (cada ponto corresponde ao faturamento diário de um dia).
        - A linha azul representa a tendência diária do faturamento.
        - Os pontos representam os dados coletados nos PDFs de pedidos."""
        user_data2 = {"titulo": titulo, "texto": texto}
        main_window.botao_ajuda(sender,app_data,user_data=user_data2) 
        
        
    @staticmethod
    def top_ajuda(sender, app_data, user_data)->None:
        main_window = user_data['main_window']
        titulo = "Ajuda: Top 5 clientes por faturamento"
        texto = """Este gráfico mostra os 5 clientes com maior faturamento total.
        - O eixo X representa os clientes (cada barra corresponde a um cliente).
        - O eixo Y representa o valor total faturado por cliente (cada barra corresponde ao valor total faturado por um cliente).
        - As barras são ordenadas do maior para o menor valor faturado."""
        user_data2 = {"titulo": titulo, "texto": texto}
        main_window.botao_ajuda(sender,app_data,user_data=user_data2)

    @staticmethod
    def kpi_ajuda(sender, app_data, user_data)->None:
        main_window = user_data['main_window']
        titulo = "Ajuda: KPIs do Dashboard"
        texto = """
        Este painel mostra os principais indicadores de desempenho (KPIs) do varejo:
        - Total de Pedidos: Quantidade absoluta de vendas realizadas no período.
        - Faturamento Total: Soma de todos os valores recebidos (receita bruta).
        - Ticket Médio: Valor médio gasto por cliente em cada compra (Faturamento / Pedidos).
        - IPT (Itens por Ticket): Média de produtos levados em cada venda. Mede a eficiência em oferecer produtos adicionais.
        - PMI (Preço Médio do Item): Valor médio de cada mercadoria vendida. Indica se o giro está focado em produtos caros ou baratos.
        O gráfico de barras apresenta os 5 maiores clientes, ordenados do maior para o menor faturamento.
        O gráfico de linhas apresenta a tendência diária do faturamento.
        """
        user_data2 = {"titulo": titulo, "texto": texto}
        main_window.botao_ajuda(sender,app_data,user_data=user_data2)
    
    
    @staticmethod
    def exportar_dados(sender, app_data, user_data)->None:
        pipeline = AppState.pipeline
        pipeline.export_and_erase_db()
        