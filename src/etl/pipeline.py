from pathlib import Path
from .extractor import PedidoPDFExtractor
from storage.repository import DatabaseRepository
from config import PATH_INPUT
from logger import LoggerMaker
from ui.state import AppState
import os
from .normalizer import *

class PedidoPipeline:
    def __init__(self,repository: DatabaseRepository):
        self.repository = repository
        self.logger = LoggerMaker().get_logger()
    
    #pipeline aqui: varrer a input, pegar o primeiro pdf, extrair os dados, comparar com o banco, atualizar o banco de dados,informar o sucesso ou falha da operação, atualizar a tela)    
    def varrer_input(self):
        self.logger.info("Iniciando processo de varredura da pasta de input")
        
        input_path = Path(PATH_INPUT)

        if not input_path.exists():
            self.logger.warning("Pasta de input não existe")
            os.mkdir(input_path)

        pdfs = list(input_path.glob("*.pdf"))

        if not pdfs:
            self.logger.warning("Nenhum PDF encontrado na pasta de input")
            return None

        for pdf_path in pdfs:
            try:
                self._processar_pdf(pdf_path)
            except Exception as e:
                self.logger.exception(
                    f"Erro ao processar o PDF {pdf_path.name}"
                )

    def _processar_pdf(self, pdf_path: Path):
        self.logger.info(f"Iniciando processamento do PDF: {pdf_path.name}")

        extractor = PedidoPDFExtractor(pdf_path)
        data = extractor.extract()

        # --- normalização ---
        pedido = PedidoNormalizer().normalize(data["pedido"])
        cliente = ClienteNormalizer().normalize(data["cliente"])
        emitente = EmitenteNormalizer().normalize(data["emitente"])
        total = ValorTotalNormalizer().normalize(data["total"])
        itens = [ItemNormalizer().normalize(i) for i in data["itens"]]

        # --- persistência ---


        cliente_db = self.repository.get_or_create_cliente(cliente)
        emitente_db = self.repository.get_or_create_emitente(
            razao_social=emitente["razao_social"],
            cnpj=emitente["cnpj"],
        )

        
        
        dados_pedido = {
            "cliente_id": cliente_db,
            "document_id": self.repository.get_or_create_document(filename=pdf_path.name,status="PROCESSED", numero_pedido=pedido["numero_pedido"]),
            "emitente_id": emitente_db,
            "numero_pedido": pedido["numero_pedido"],
            "data_venda": pedido["data_venda"],
            "condicao_pagamento": pedido["condicao_pagamento"],
            "total_sem_impostos": total["total_sem_impostos"],
            "ipi": total["ipi"],
            "st": total["st"],
            "frete": total["frete"],
            "desconto_total": total["desconto_total"],
            "total_final": float(total["total_final"]),
        }
        pedido_db, created = self.repository.get_or_create_pedido(
                dados=dados_pedido
            )

        if created:
            self.repository.insert_itens_pedido(pedido_db, itens)
            

        self.logger.info(
            f"PDF {pdf_path.name} processado com sucesso "
            f"(Pedido {pedido['numero_pedido']})"
        )
    
    def listar_pedidos(self)->dict:
        pedidos = self.repository.listar_pedidos()
        pipeline = PedidoPipeline(self.repository)
        AppState.pipeline = pipeline
        return pedidos 
        
        
    def gerar_dashboard_data(self):
        try:
            res = self.repository.obter_metricas_dashboard()
            
            # Pega os totais para os KPIs
            geral = res.get('geral', {})
            faturamento = geral.get('faturamento_total', 0) or 0
            pedidos = geral.get('total_pedidos', 0) or 0
            itens = geral.get('total_itens', 0) or 0

            kpis = {
                "faturamento_total": faturamento,
                "total_pedidos": pedidos,
                "ticket_medio": faturamento / pedidos if pedidos > 0 else 0,
                "ipt": itens / pedidos if pedidos > 0 else 0,
                "pmi": faturamento / itens if itens > 0 else 0
            }

            # Organiza os dados para os gráficos
            graficos = {
                "faturamento_diario": res.get('evolucao', []),
                "top_clientes": res.get('clientes', [])
            }

            return kpis, graficos
        except Exception as e:
            self.logger.error(f"Erro: {e}")
            return {}, {"faturamento_diario": [], "top_clientes": []}

    def _retorno_vazio(self):
        return {
            "faturamento_total": 0.0,
            "total_pedidos": 0,
            "ticket_medio": 0.0,
            "ipt": 0.0,
            "pmi": 0.0
        }
            
            
    
            