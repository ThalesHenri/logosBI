"""
    Esse arquivo precisa:
        - buscar os pdfs na pasta input
        - extrair o texto do pdf
        - retornar o texto de forma bruta

"""
import pdfplumber
import re

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
    def _is_item_valid(self,item) -> bool:
        try:
            # numeracao precisa ser inteiro puro
            if not item["numeracao"].isdigit():
                return False

            # codigo precisa ser inteiro
            if not item["codigo"].isdigit():
                return False

            # descrição obrigatória e não numérica
            descricao = item["descricao"].strip()
            if not descricao or descricao.replace(",", "").replace(".", "").isdigit():
                return False

            # quantidade > 0
            qtd = float(item["quantidade"].replace(",", "."))
            if qtd <= 0:
                return False

            # valor unitário > 0
            vu = float(item["valor_unitario"].replace(",", "."))
            if vu <= 0:
                return False

            # total coerente
            total = float(item["valor_total"].replace(",", "."))
            if round(qtd * vu, 2) != round(total, 2):
                return False

            return True

        except Exception:
            return False

        
        
    
    def _search(self,pattern,text):
        match = re.search(pattern,text)
        return match.group(1).strip() if match else None