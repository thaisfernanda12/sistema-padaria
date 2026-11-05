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
            quantidade INTEGER NOT NULL,
            estoque_minimo INTEGER NOT NULL DEFAULT 5
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

    colunas = [coluna[1] for coluna in cursor.execute(
        "PRAGMA table_info(produtos)"
    ).fetchall()]

    if "estoque_minimo" not in colunas:
        cursor.execute("""
            ALTER TABLE produtos
            ADD COLUMN estoque_minimo INTEGER NOT NULL DEFAULT 5
        """)

    conexao.commit()
    conexao.close()