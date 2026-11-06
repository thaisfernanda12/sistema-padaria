import sqlite3
import database


def test_criar_tabelas(monkeypatch, tmp_path):
    caminho = tmp_path / "teste.db"

    monkeypatch.setattr(
        database,
        "conectar",
        lambda: sqlite3.connect(caminho)
    )

    database.criar_tabela()

    conexao = sqlite3.connect(caminho)
    cursor = conexao.cursor()

    tabelas = cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type = 'table'
    """).fetchall()

    nomes = [tabela[0] for tabela in tabelas]

    assert "produtos" in nomes
    assert "vendas" in nomes

    conexao.close()


def test_adicionar_estoque_minimo(monkeypatch, tmp_path):
    caminho = tmp_path / "teste_antigo.db"

    conexao = sqlite3.connect(caminho)
    conexao.execute("""
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()

    monkeypatch.setattr(
        database,
        "conectar",
        lambda: sqlite3.connect(caminho)
    )

    database.criar_tabela()

    conexao = sqlite3.connect(caminho)
    colunas = [
        coluna[1]
        for coluna in conexao.execute(
            "PRAGMA table_info(produtos)"
        ).fetchall()
    ]

    assert "estoque_minimo" in colunas

    conexao.close()