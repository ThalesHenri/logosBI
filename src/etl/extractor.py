"""
    Esse arquivo precisa:
        - buscar os pdfs na pasta input
        - extrair o texto do pdf
        - retornar o texto de forma bruta

"""
import pdfplumber
import re
from logger import LoggerMaker

logger = LoggerMaker().get_logger()

class PedidoPDFExtractor:
    def __init__(self,pdf_path):
        self.pdf_path = pdf_path
        
    def extract(self):
        text = self._extract_text()
        itens = self._extract_itens()
        cliente = self._extract_cliente(text)
        emitente = self._extract_emitente(text)
        pedido = self._extract_pedido(text)
        total = self._extract_valor_total(text)
        return {
            "text": text,
            "itens": itens,
            "cliente": cliente,
            "emitente": emitente,
            "pedido": pedido,
            "total": total,
        }
        
    #metodos privados
    
    #extração bruta
    def _extract_text(self):
        full_text = ""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        return full_text
    
    #extrações especificas
    def _extract_emitente(self,text):
        return {
            "razao_social": self._search(r"Indústria:\s*(.+)",text),
            "cnpj":self._search(r"CNPJ da Indústria:\s*([\d./-]+)",text),
        }


    def _extract_cliente(self,text):
        return{
            "razao_social":self._search(r"Razão Social:\s*(.+)",text),
            "documento":self._search(r"CNPJ/CPF:\s*([\d./-]+)",text),
            "nome_fantasia":self._search(r"Nome Fantasia:\s*(.+)",text),
            "endereco":self._search(r"Endereço:\s*(.+)",text),
            "telefone":self._search(r"Telefone:\s*(.+)",text),
            "email":self._search(r"E-mail:\s*(.+)",text),
        }
        
    
    def _extract_pedido(self,text):
        return {
            "numero_pedido":self._search(r"Informações sobre PEDIDO - Nº\s*(\d+)",text),#"Informações sobre PEDIDO - N°:\s*(\d+)" \s*(.+)",text),
            "data_venda": self._search(r"Data da Venda:\s*(\d{2}/\d{2}/\d{4})",text),
            "condicao_pagamento":self._search(r"Condição de Pagto:\s*(.+)",text),
        }
        
    
    def _extract_valor_total(self, text: str) -> dict | None:
        #extraindo as linhas
        linhas = [l.strip() for l in text.splitlines() if l.strip()]
        
        #buscando a linha que tem o valor total
        for i,linha in enumerate(linhas):
            if linha.startswith("Total s/ impostos"):
                if i + 1< len(linhas):
                    valores = linhas[i + 1].split()
                
                #sei que a tabela tem 7 colunas    
                    if len(valores) >= 7:
                       return {
                           "total_sem_impostos": valores[0],
                           "qtd_itens": valores[1],
                           "peso_liquido": valores[2],
                           "ipi": valores[3],
                           "st": valores[4],
                           "frete": valores[5],
                           "total_final": valores[6],
                       }
    
    
    def _debug_text(self, text:str) -> None:
        print("===== TEXTO EXTRAÍDO DO PDF =====")
        for i, linha in enumerate(text.splitlines()):
            print(f"{i:03d}: {linha}")
        print("================================")
    
    def _extract_itens(self):
        itens = []
        itens_validados = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    for row in table[1:]:#pulando o cabeçalho por isso o [1:]
                        try:
                            itens.append({
                                "numeracao":row[0],
                                "codigo":row[1],
                                "descricao":row[2],
                                "quantidade":row[3],
                                "valor_unitario":row[4],
                                "percentual_desconto":row[5],
                                "valor_total":row[6],
                            })
                        except IndexError:
                            continue
        
        for item in itens:
            if self._is_item_valid(item):
                itens_validados.append(item)
            else:
                print(f"Item inválido encontrado e ignorado: {item}")
        
        return itens_validados
     
    
    #validação de item
    def _is_item_valid(self, item) -> bool:
        try:
            # 1. Função auxiliar interna para converter números com segurança
            def parse_num(val):
                if not val: return 0.0
                # Remove pontos de milhar e troca vírgula por ponto
                limpo = str(val).replace('.', '').replace(',', '.')
                try: return float(limpo)
                except: return 0.0

            # 2. Extração e Limpeza dos campos
            numeracao = item.get("numeracao", "").strip()
            codigo = item.get("codigo", "").strip()
            descricao = item.get("descricao", "").strip()
            
            qtd = parse_num(item.get("quantidade", "0"))
            vu = parse_num(item.get("valor_unitario", "0"))
            total = parse_num(item.get("valor_total", "0"))

            # 3. CRITÉRIOS DE VALIDAÇÃO FLEXÍVEIS:
            
            # A - Descrição é o coração do item. Se não houver texto, não é um produto.
            if not descricao or len(descricao) < 3:
                return False

            # B - Se não tem quantidade nem valor total, provavelmente é ruído do PDF
            if qtd <= 0 and total <= 0:
                return False

            # C - Verificação de Código/Numeração: 
            # Em vez de isdigit(), apenas removemos sujeira. 
            # Se sobrar algo, consideramos válido.
            if not any(char.isdigit() for char in (numeracao + codigo)):
                # Se não tem nem número nem código, pode ser uma linha de observação
                return False

            # D - CONSISTÊNCIA (Opcional): 
            # Em vez de travar o processo, apenas logamos se o total estiver estranho,
            # mas permitimos que o item entre (confiamos no total impresso no PDF).
            if vu > 0 and qtd > 0:
                calculado = round(qtd * vu, 2)
                diferenca = abs(calculado - round(total, 2))
                if diferenca > 0.05: # Tolera 5 centavos de erro de arredondamento
                    logger.warning(f"Divergência de centavos no item {codigo}: Calc {calculado} vs PDF {total}")

            return True

        except Exception as e:
            logger.error(f"Erro crítico na validação de item: {e}")
            return False

        
        
    
    def _search(self,pattern,text):
        match = re.search(pattern,text)
        return match.group(1).strip() if match else None