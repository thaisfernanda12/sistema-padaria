import sqlite3

def conectar():
    return sqlite3.connect("padaria.db")

def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_total REAL NOT NULL,
            data_venda TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    conexao.commit()
    conexao.close()