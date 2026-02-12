import dearpygui.dearpygui as dpg
from .callbacks import Callbacks
from logger import LoggerMaker

logger = LoggerMaker().get_logger()

class MainWindow:
    def __init__(self, label: str, tag: str) -> None:
        """Classe responsável por criar toda a interfaçe grafica.
            É conceitualmente chamada pela classe Callback.

        Args:
            label (str): Nome da janela
            tag (str): Tag única da janela, usada para referenciar a janela em callbacks e atualizações de UI
        """
        self.label = label
        self.tag = tag
        self.build()

    def build(self) -> None:
        with dpg.window(
            label=self.label,
            tag=self.tag,
            no_title_bar=True,
            no_move=True,
            no_collapse=True,
        ):
            self._header()
            
            # --- SISTEMA DE ABAS ---
            with dpg.tab_bar(tag="main_tabs"):
                
                # ABA 1: OPERACIONAL
                with dpg.tab(label="Operacional",tag="tag_operacional"):
                    self._pedidos_table()
                
                # ABA 2: DASHBOARD (Gráficos e KPIs)
                with dpg.tab(label="Dashboard",tag="tag_dashboard"):
                    self._dashboard_view()

        dpg.set_primary_window(self.tag, True)

    # =========================
    # 📊 DASHBOARD COMPONENTS
    # =========================
    def _dashboard_view(self)->None:
        

        dpg.add_spacer(height=10)
        
        # --- SEÇÃO DE KPIs (Cards Rápidos) ---
        with dpg.group(horizontal=True):
            dpg.add_button(label="Atualizar Dashboard", callback=Callbacks.atualizar_dashboard,user_data={"main_window": self, "aba_ativa": "tag_dashboard"}, width=150)
            dpg.add_button(
                label="?",
                callback=Callbacks.kpi_ajuda,
                user_data={"main_window": self}
            )
            dpg.add_separator
        
        with dpg.group(horizontal=True):
            with dpg.child_window(width=200, height=80, border=True):
                dpg.add_text("Total Pedidos")
                dpg.add_text("0", tag="kpi_total_pedidos", color=[0, 255, 0])
            
            with dpg.child_window(width=200, height=80, border=True):
                dpg.add_text("Faturamento Total")
                dpg.add_text("R$ 0.00", tag="kpi_faturamento_total", color=[0, 255, 0])

            with dpg.child_window(width=200, height=80, border=True):
                dpg.add_text("Ticket Médio")
                dpg.add_text("R$ 0.00", tag="kpi_ticket_medio", color=[0, 255, 0])

            with dpg.child_window(width=200, height=80, border=True):
                dpg.add_text("IPT")
                dpg.add_text(" Itens / Pedido: 0.00", tag="kpi_ipt", color=[0, 255, 0])

            with dpg.child_window(width=200, height=80, border=True):
                dpg.add_text("PMI")
                dpg.add_text("R$ 0.00", tag="kpi_pmi", color=[0, 255, 0])

        dpg.add_spacer(height=20)
        dpg.add_separator()
        dpg.add_spacer(height=10)

        # --- GRÁFICO DE TENDÊNCIA ---
        dpg.add_text("Tendência de Faturamento Diário", bullet=True)
        dpg.add_button(
            label="?",
            callback=Callbacks.faturamento_ajuda,
            user_data={"main_window": self}
        )
        with dpg.plot(label="Faturamento por Dia", height=400, width=-1, tag="dashboard_plot"):
            dpg.add_plot_legend()
            
            # Eixo X (Tempo/Dias)
            dpg.add_plot_axis(dpg.mvXAxis, label="Dias (Sequencial)", tag="x_axis")
            
            # Eixo Y (Dinheiro)
            dpg.add_plot_axis(dpg.mvYAxis, label="Valor (R$)", tag="y_axis")
            
            # Série de Dados (Linha)
            dpg.add_line_series([], [], label="Faturamento", parent="y_axis", tag="series_faturamento")

        #--- Grafico Top Clientes ---
        dpg.add_text("Top 5 Clientes por Faturamento", bullet=True)
        dpg.add_button(
            label="?",
            callback=Callbacks.top_ajuda,
            user_data={"main_window": self}
        )
        with dpg.plot(no_title=True, height=400, width=-1, tag="dashboard_clientes_plot"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Total (R$)", tag="x_axis_clientes")
            with dpg.plot_axis(dpg.mvYAxis, label="Lojas", tag="y_axis_clientes"):
                dpg.add_bar_series([], [], label="Faturamento", tag="series_clientes",horizontal=True, weight=0.5)
    # 🔄 ATUALIZAÇÃO DE TELAS
    # =========================
    def atualizar_tela_principal(self, pedidos) -> None:
        if not pedidos:
            logger.warning("Nenhum pedido para exibir")
            return

        if not dpg.does_item_exist("pedidos_table"):
            return

        # Limpa as linhas antigas
        for table in ["pedidos_table", "itens_pedidos_table"]:
            rows = dpg.get_item_children(table, 1) or []
            for row in rows:
                dpg.delete_item(row)

        for pedido_bruto in pedidos:
            pedido = dict(pedido_bruto) if hasattr(pedido_bruto, "keys") else pedido_bruto
            with dpg.table_row(parent="pedidos_table"):
                dpg.add_selectable(
                    label=str(pedido.get("numero_pedido", "-")),
                    user_data={"main_window": self, "pedido_id": pedido.get("id", -1)},
                    callback=Callbacks.selecionar_pedido
                )
                dpg.add_text(str(pedido.get("data_venda", "-")))
                dpg.add_text(str(pedido.get("cliente", "-"))) # Corrigido para razao_social conforme conversas anteriores
                dpg.add_text(f"R$ {float(pedido.get('total_sem_impostos', 0)):.2f}")
                dpg.add_text(f"R$ {float(pedido.get('total_final', 0)):.2f}")

    def atualizar_tela_itens(self, itens)->None:
        if dpg.does_item_exist("itens_pedidos_table"):
            rows = dpg.get_item_children("itens_pedidos_table", 1) or []
            for row in rows:
                dpg.delete_item(row)

        if not itens:
            return

        for item_bruto in itens:
            item = dict(item_bruto) if hasattr(item_bruto, "keys") else item_bruto
            with dpg.table_row(parent="itens_pedidos_table"):
                dpg.add_text(str(item.get("codigo", ""))) # Chave corrigida conforme seu normalizer
                dpg.add_text(str(item.get("descricao", "")))
                dpg.add_text(str(item.get("quantidade", "")))
                dpg.add_text(f"R$ {float(item.get('valor_unitario', 0)):.2f}")
                dpg.add_text(f"R$ {float(item.get('valor_total', 0)):.2f}")

    # Método para atualizar os gráficos e KPIs
    def atualizar_dashboard_ui(self, dados_kpi: dict, dados_grafico: list):
        """
        Atualiza os elementos definidos no dashboard em _dashboard_view() com 
        os seus respectivos dados.

        Args:
            dados_kpi (dict): _description_
            dados_grafico (list): _description_
        """
        # ==========================================
        # 1. ATUALIZAÇÃO DOS CARDS (KPIs)
        # ==========================================
        dpg.set_value("kpi_total_pedidos", str(dados_kpi.get("total_pedidos", 0)))
        dpg.set_value("kpi_faturamento_total", f"R$ {dados_kpi.get('faturamento_total', 0):.2f}")
        dpg.set_value("kpi_ticket_medio", f"R$ {dados_kpi.get('ticket_medio', 0):.2f}")
        dpg.set_value("kpi_ipt", f"Itens / Pedido: {dados_kpi.get('ipt', 0):.2f}")
        dpg.set_value("kpi_pmi", f"R$ {dados_kpi.get('pmi', 0):.2f}")

        # ==========================================
        # 2. GRÁFICO 1: TENDÊNCIA DIÁRIA (LINHA)
        # ==========================================
        diario = dados_grafico.get("faturamento_diario", [])
        if diario:
            x_diario = [float(i) for i in range(len(diario))]
            y_diario = [float(d.get('faturamento', 0)) for d in diario]

        dpg.set_value("series_faturamento", [x_diario, y_diario])
        dpg.fit_axis_data("x_axis")
        dpg.fit_axis_data("y_axis")

        # ==========================================
        # 3. GRÁFICO 2: TOP 5 CLIENTES (BARRAS)
        # ==========================================
        clientes = dados_grafico.get("top_clientes", [])
        if clientes:
            # Extraímos nomes para as etiquetas e valores para as barras
            nomes_clientes = [c.get('cliente', 'Desconhecido') for c in clientes]
            valores_clientes = [float(c.get('total', 0)) for c in clientes]

            # Índices numéricos para o DPG posicionar as barras
            x_indices = [float(i) for i in range(len(valores_clientes))]

            # Atualiza a série de barras: [x, y]
            dpg.set_value("series_clientes", [valores_clientes, x_indices])

            # Ajuste de escala do grafico
            dpg.set_axis_limits("x_axis_clientes", 0, max(valores_clientes) * 1.2 if valores_clientes else 10)

            # garante que o nome do cliente seja exibido no eixo X
            dpg.fit_axis_data("y_axis_clientes")

            # --- O PULO DO GATO ---
            # Substitui os números 0, 1, 2 no eixo X pelos nomes dos clientes
            ticks = []
            for i, nome in enumerate(nomes_clientes):
                ticks.append((nome, i))

            dpg.set_axis_ticks("y_axis_clientes", tuple(ticks))

            # Ajusta o zoom para os novos dados
            dpg.fit_axis_data("x_axis_clientes")
            dpg.fit_axis_data("y_axis_clientes")

    # =========================
    # 🧱 UI COMPONENTS
    # =========================
    def _header(self):
        dpg.add_text("LogosBI - Business Intelligence para Pedidos", tag="header_text")
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Importar PDFs", callback=Callbacks.importar_pdf, width=150)
            dpg.add_button(label="Atualizar Dados", callback=Callbacks.dados_gerados, user_data=self, width=150)
        dpg.add_spacer(height=10)
        dpg.add_separator()

    def _pedidos_table(self):
        dpg.add_spacer(height=10)
        dpg.add_text("Lista de Pedidos (Clique no número para detalhes)", color=[200, 200, 200])
        with dpg.table(tag="pedidos_table", header_row=True, resizable=True, row_background=True,
                       borders_innerH=True, borders_outerH=True, height=250):
            dpg.add_table_column(label="Pedido")
            dpg.add_table_column(label="Data")
            dpg.add_table_column(label="Cliente")
            dpg.add_table_column(label="Total s/ Imp")
            dpg.add_table_column(label="Total Final")
        
        dpg.add_spacer(height=20)
        dpg.add_text("Itens do Pedido Selecionado", color=[200, 200, 200])
        with dpg.table(tag="itens_pedidos_table", header_row=True, resizable=True, row_background=True,
                       borders_innerH=True, borders_outerH=True, height=-1):  
            dpg.add_table_column(label="Código")
            dpg.add_table_column(label="Descrição")
            dpg.add_table_column(label="Qtd")
            dpg.add_table_column(label="V. Unit")
            dpg.add_table_column(label="V. Total")
            
    def botao_ajuda(self, sender, app_data, user_data)->None:
        titulo = user_data["titulo"]
        texto = user_data["texto"]
        
        if dpg.does_item_exist("popup_ajuda"):
            dpg.delete_item("popup_ajuda")
        
        with dpg.window(
            label = titulo,
            tag="popup_ajuda",
            no_collapse=True,
        ):
            dpg.add_text(texto, wrap=800)
            dpg.add_spacer(height=10)
            dpg.add_button(label="Fechar", width=100, callback=lambda: dpg.delete_item("popup_ajuda"))