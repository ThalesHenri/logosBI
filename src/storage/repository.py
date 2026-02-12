import sqlite3
from config import DB_PATH


class DatabaseRepository:
    def __init__(self):
        self.conn = None
        self.cursor = None
    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    def close(self):
        self.conn.close()
    
    def create_schema(self):
        

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            numero_pedido TEXT,
            origem TEXT DEFAULT 'SuasVendas',
            status TEXT CHECK(status IN ('PROCESSED', 'FAILED')) NOT NULL,
            data_processamento DATETIME DEFAULT CURRENT_TIMESTAMP,
            erro TEXT
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS emitentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT NOT NULL,
            cnpj TEXT UNIQUE NOT NULL,
            tabela_preco TEXT
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT NOT NULL,
            nome_fantasia TEXT,
            documento TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT
           
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            emitente_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            numero_pedido TEXT NOT NULL,
            data_venda DATE NOT NULL,
            condicao_pagamento TEXT,
            total_sem_impostos REAL,
            total_ipi REAL,
            total_st REAL,
            total_frete REAL,
            desconto_total REAL,
            total_final REAL,
            quantidade_itens INTEGER,
            peso_liquido REAL,
            peso_total REAL,
            FOREIGN KEY (document_id) REFERENCES documents(id),
            FOREIGN KEY (emitente_id) REFERENCES emitentes(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            codigo_produto TEXT,
            descricao TEXT NOT NULL,
            quantidade REAL NOT NULL,
            valor_unitario REAL NOT NULL,
            percentual_desconto REAL,
            valor_total REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        );
        """)

        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pedidos_data
        ON pedidos(data_venda);
        """)

        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido
        ON itens_pedido(pedido_id);
        """)

        self.conn.commit()

    
    def get_or_create_document(self,filename:str, status:str, numero_pedido:str=None, erro:str=None)->int:
        #faz uma consulta para verificar se o documento já existe
        self.cursor.execute("""
            SELECT id FROM documents WHERE filename = ?
        """,(filename,))
        row = self.cursor.fetchone()
        if row:
            return row['id']
        
        self.cursor.execute("""
            INSERT INTO documents(filename,numero_pedido,status,erro) 
            VALUES (?,?,?,?)
        """,(filename,numero_pedido,status,erro))
        self.conn.commit()
        return self.cursor.lastrowid
    

    def get_or_create_emitente(self,razao_social,cnpj,tabela_preco=None):
        #verificar se ja exiteste emitentes com esse cnpj
        self.cursor.execute("""
           SELECT id FROM emitentes WHERE cnpj = ? 
        """,(cnpj,))
        row = self.cursor.fetchone()
        if row:
            return row['id']
        
        self.cursor.execute("""
            INSERT INTO emitentes(
                razao_social,
                cnpj,
                tabela_preco
            ) VALUES (?,?,?)
        """,(razao_social,cnpj,tabela_preco))
        
        self.conn.commit()
        return self.cursor.lastrowid
    

    def get_or_create_cliente(self,dados):
        documento = dados.get("documento")
        nome_fantasia = dados.get("nome_fantasia")
        razao_social = dados.get("razao_social")
        telefone = dados.get("telefone")
        email = dados.get("email")
        endereco = dados.get("endereco")
        if not documento:
            raise ValueError("Clientes sem documentos não podem ser cadastrados")
        
        self.cursor.execute("""
           SELECT id FROM clientes WHERE documento = ? 
        """,(documento,))
        row = self.cursor.fetchone()
        if row:
            return row['id']
        
        
        self.cursor.execute("""
            INSERT INTO clientes(
                razao_social,
                nome_fantasia,
                documento,
                telefone,
                email,
                endereco
            ) VALUES (?,?,?,?,?,?)
        """,(razao_social,nome_fantasia,documento,telefone,email,endereco))
        self.conn.commit()
        return self.cursor.lastrowid
    
    
    def get_or_create_pedido(self, dados):
        numero_pedido = dados.get("numero_pedido")
        if not numero_pedido:
            raise ValueError("Pedidos sem número não podem ser cadastrados")
        
        self.cursor.execute("""
           SELECT id FROM pedidos WHERE numero_pedido = ? 
        """,(numero_pedido,))
        row = self.cursor.fetchone()
        if row:
            return row['id'], False
        
        self.cursor.execute("""
            INSERT INTO pedidos(
                document_id,
                emitente_id,
                cliente_id,
                numero_pedido,
                data_venda,
                condicao_pagamento,
                total_sem_impostos,
                total_ipi,
                total_st,
                total_frete,
                desconto_total,
                total_final
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
            dados.get("document_id"),
            dados.get("emitente_id"),
            dados.get("cliente_id"),
            numero_pedido,
            dados.get("data_venda"),
            dados.get("condicao_pagamento"),
            dados.get("total_sem_impostos"),
            dados.get("total_ipi"),
            dados.get("total_st"),
            dados.get("total_frete"),
            dados.get("desconto_total"),
            dados.get("total_final")
        ))
        self.conn.commit()
        return (self.cursor.lastrowid, True)
                            
                            
    def insert_itens_pedido(self,pedido_id, itens):
        #extrai os dados
        if not itens:
            raise ValueError("Pedido sem itens")
        for item in itens:
            codigo_produto = item.get("codigo_produto")
            descricao = item.get("descricao")
            quantidade = item.get("quantidade")
            valor_unitario = item.get("valor_unitario")
            valor_total = item.get("valor_total")
            percentual_desconto = item.get("percentual_desconto")
            valor_total = item.get("valor_total")
            
            self.cursor.execute("""
            INSERT INTO itens_pedido(
                pedido_id,
                codigo_produto,
                descricao,
                quantidade,
                valor_unitario,
                percentual_desconto,
                valor_total
            ) VALUES (?,?,?,?,?,?,?)
            """,(
                pedido_id,
                codigo_produto,
                descricao,
                quantidade,
                valor_unitario,
                percentual_desconto,
                valor_total
            ))
            
        self.conn.commit()
        
        # insere no banco
        
    
    def listar_pedidos(self):
        query = """
        SELECT 
            p.id,
            p.numero_pedido,
            c.razao_social AS cliente,
            p.total_final,
            p.data_venda,
            p.total_sem_impostos
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.data_venda DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    
    def listar_itens_pedido(self, pedido_id):
        query = """
        SELECT 
            codigo_produto,
            descricao,
            quantidade,
            valor_unitario,
            percentual_desconto,
            valor_total
        FROM itens_pedido
        WHERE pedido_id = ?
        """
        self.cursor.execute(query, (pedido_id,))
        return self.cursor.fetchall()
        
        
    def obter_metricas_dashboard(self)->dict:
        """Faz uma consulta ao banco de dados para ober os dados necessarios para o dashboard. 
        Idealmente, o repositório deve retornar um dicionário organizado com as seguintes chaves:
        - geral: dict com os KPIs principais (faturamento_total, total_pedidos, total_itens)
        - evolucao: lista de dicts com a evolução diária do faturamento (dia, faturamento, qtd_pedidos)
        - clientes: lista de dicts com os top clientes (cliente, total)

        Returns:
            dict: _description_
        """
    
    
    # 1. Query do Faturamento
        query_evolucao = """
        SELECT 
            date(data_venda) as dia,
            SUM(total_final) AS faturamento,
            COUNT(id) AS qtd_pedidos
        FROM pedidos
        GROUP BY dia
        ORDER BY dia ASC
        """
        
        # 2. Query de Top Clientes (Para o gráfico de barras)
       
        query_clientes = """
        SELECT c.razao_social as cliente, SUM(total_final) as total
        FROM pedidos 
        JOIN clientes c ON pedidos.cliente_id = c.id
        GROUP BY c.id, c.razao_social
        ORDER BY total DESC
        LIMIT 5
        """

        # 3. Query de Totais (Para os Cards de KPI)
        query_totais = """
        SELECT 
            SUM(total_final) as faturamento_total,
            COUNT(id) as total_pedidos,
            (SELECT SUM(quantidade) FROM itens_pedido) as total_itens
        FROM pedidos
        """

        # Execução
        self.cursor.execute(query_evolucao)
        evolucao = [dict(row) for row in self.cursor.fetchall()]
        
        self.cursor.execute(query_clientes)
        clientes = [dict(row) for row in self.cursor.fetchall()]
        
        self.cursor.execute(query_totais)
        linha_total = self.cursor.fetchone()
        totais = dict(linha_total) if linha_total else {}

        # Retornamos um único dicionário organizado
        return {
            "geral": totais,
            "evolucao": evolucao,
            "clientes": clientes
        }
    