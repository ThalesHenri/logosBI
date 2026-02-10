"""
Sabendo que tudo o que é extraido do PDF pode conter erros e ainda,
por cima chega em string, o normalizador tem a função de validar e converter os dados para os tipos corretos, 
além de lidar com possíveis erros de extração, como campos faltando ou formatados incorretamente. 
Ele atua como uma camada de limpeza e preparação dos dados antes que sejam usados para análises ou armazenados no banco de dados.

"""
from decimal import Decimal 
from datetime import datetime


class BaseNormalizer:
    @staticmethod
    def to_decimal(value:str) -> Decimal:
        try:
            #removendo o símbolo de moeda e convertendo para Decimal
            return Decimal(value.replace("R$", "").replace(".", "").replace(",", ".").strip())
        except Exception as e:
            print(f"Erro ao converter '{value}' para Decimal: {e}")
            return Decimal(0)
    
    @staticmethod
    def to_date(value:str) -> datetime:
        try:
            return datetime.strptime(value.strip(), "%d/%m/%Y")
        except Exception as e:
            print(f"Erro ao converter '{value}' para datetime: {e}")
            return None
        
        
    @staticmethod
    def to_float(value:str) -> float:
        try:
            return float(value.strip().replace(",", "."))
        except Exception as e:
            print(f"Erro ao converter '{value}' para float: {e}")
            return 0.0
        
    @staticmethod
    def to_int(value:str) -> int:
        try:
            return int(value.strip())
        except Exception as e:
            print(f"Erro ao converter '{value}' para int: {e}")
            return 0
        
        
    @staticmethod
    def clean_text(value:str) -> str:
        return value.strip() if value else ""
    
    
class PedidoNormalizer(BaseNormalizer):
    def normalize(self, pedido_raw:dict)->dict:
        return {
            "numero_pedido": self.clean_text(pedido_raw.get("numero_pedido", "")),
            "data_venda": self.to_date(pedido_raw.get("data_venda", "")),
            "condicao_pagamento": self.clean_text(pedido_raw.get("condicao_pagamento", "")),
        }
        
class ClienteNormalizer(BaseNormalizer):
    def normalize(self, cliente_raw:dict)->dict:
        return {
            "razao_social": self.clean_text(cliente_raw.get("razao_social", "")),
            "documento": self.clean_text(cliente_raw.get("documento", "")),
            "nome_fantasia": self.clean_text(cliente_raw.get("nome_fantasia", "")),
            "endereco": self.clean_text(cliente_raw.get("endereco", "")),
            "telefone": self.clean_text(cliente_raw.get("telefone", "")),
            "email": self.clean_text(cliente_raw.get("email", "")),
        }
        
class EmitenteNormalizer(BaseNormalizer):
    def normalize(self, emitente_raw:dict)->dict:
        return {
            "razao_social": self.clean_text(emitente_raw.get("razao_social", "")),
            "cnpj": self.clean_text(emitente_raw.get("cnpj", "")),
        }
        
        
class ItemNormalizer(BaseNormalizer):
    def normalize(self, item_raw:dict)->dict:
        return {
            "codigo": self.clean_text(item_raw.get("codigo", "")),
            "descricao": self.clean_text(item_raw.get("descricao", "")),
            "quantidade": self.to_int(item_raw.get("quantidade", "0")),
            "valor_unitario": self.to_float(item_raw.get("valor_unitario", "0")),
            "percentual_desconto": self.to_float(item_raw.get("percentual_desconto", "0")),
            "valor_total": self.to_float(item_raw.get("valor_total", "0")),
        }
        

class ValorTotalNormalizer(BaseNormalizer):
    def normalize(self, valor_total_raw:dict)->dict:
        return {
            "total_sem_impostos": self.to_float(valor_total_raw.get("total_sem_impostos", "0")),
            "ipi": self.to_float(valor_total_raw.get("ipi", "0")),
            "st": self.to_float(valor_total_raw.get("st", "0")),
            "frete": self.to_float(valor_total_raw.get("frete", "0")),
            "desconto_total": self.to_float(valor_total_raw.get("desconto_total", "0")),
            "total_final": self.to_float(valor_total_raw.get("total_final", "0")),
        }
