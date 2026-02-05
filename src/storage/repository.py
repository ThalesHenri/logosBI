import sqlite3
from config import DB_PATH


class DatabaseRepository:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def create_schema(self):
        cursor = self.conn.cursor()

        cursor.execute("""
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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emitentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT NOT NULL,
            cnpj TEXT UNIQUE NOT NULL,
            tabela_preco TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT NOT NULL,
            nome_fantasia TEXT,
            documento TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            bairro TEXT,
            cep TEXT,
            cidade TEXT,
            uf TEXT
        );
        """)

        cursor.execute("""
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

        cursor.execute("""
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

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pedidos_data
        ON pedidos(data_venda);
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido
        ON itens_pedido(pedido_id);
        """)

        self.conn.commit()

    
    def insert_document(self,filename,numero_pedido=None,status='PROCESSED',erro=None):
        #sem passar a origem, vai ser o default sempre
        self.cursor.execute(
        """
        INSERT INTO documents(
            filename,
            numero_pedido,
            status,
            erro
        ) VALUES (?,?,?,?)
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
        bairro = dados.get("bairro")
        cep = dados.get("cep")
        cidade = dados.get("cidade")
        uf = dados.get("uf")
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
                endereco,
                bairro,
                cep,
                cidade,
                uf
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """,(razao_social,nome_fantasia,documento,telefone,email,endereco,bairro,cep,cidade,uf))
        self.conn.commit()
        return self.cursor.lastrowid
    
    
    def insert_pedido(self,dados):
        pass
    
    def close(self):
        self.conn.close()