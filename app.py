
from flask import Flask, request, redirect, render_template, render_template_string
from database import criar_tabela, conectar
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if request.method == "POST":
        nome = request.form["nome"].strip()

        if not nome:
            return "O nome do produto não pode ficar vazio."

        preco = float(request.form["preco"])
        quantidade = int(request.form["quantidade"])
        estoque_minimo = int(request.form["estoque_minimo"])

        if preco < 0 or quantidade < 0 or estoque_minimo < 0:
            return "Os valores não podem ser negativos."

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO produtos
            (nome, preco, quantidade, estoque_minimo)
            VALUES (?, ?, ?, ?)
        """, (nome, preco, quantidade, estoque_minimo))

        conexao.commit()
        conexao.close()

        return redirect("/produtos")

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM produtos")
    lista = cursor.fetchall()
    conexao.close()

    return render_template_string("""
    <style>
        body {
            font-family: Arial;
            background: #faf5ed;
            color: #493323;
            padding: 30px;
        }

        h1, h2 {
            color: #70452f;
        }

        input, button {
            padding: 10px;
            margin: 5px;
        }

        button {
            background: #a95f35;
            color: white;
            border: none;
            cursor: pointer;
        }

        table {
            background: white;
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }

        th {
            background: #70452f;
            color: white;
        }

        a {
            color: #70452f;
        }
    </style>

    <h1>Cadastro de Produtos</h1>

    <form method="POST">
        <p>Nome:</p>
        <input name="nome" required>

        <p>Preço:</p>
        <input name="preco" type="number" step="0.01" min="0" required>

        <p>Quantidade:</p>
        <input name="quantidade" type="number" min="0" required>

        <p>Estoque mínimo:</p>
        <input name="estoque_minimo" type="number" min="0" value="5" required>

        <br>
        <button type="submit">Cadastrar produto</button>
    </form>

    <h2>Estoque de Produtos</h2>

    <table>
        <tr>
            <th>Produto</th>
            <th>Preço</th>
            <th>Quantidade</th>
            <th>Situação</th>
        </tr>

        {% for produto in lista %}
        <tr>
            <td>{{ produto[1] }}</td>
            <td>R$ {{ "%.2f"|format(produto[2]) }}</td>
            <td>{{ produto[3] }}</td>
            <td>
                {% if produto[3] <= produto[4] %}
                    Estoque baixo!
                {% else %}
                    Disponível
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>

    <br>
    <a href="/">Voltar ao início</a>

""", lista=lista)


@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    conexao = conectar()
    cursor = conexao.cursor()

    if request.method == "POST":
        produto_id = int(request.form["produto_id"])
        quantidade = int(request.form["quantidade"])

        if quantidade <= 0:
            conexao.close()
            return "A quantidade deve ser maior que zero."

        cursor.execute(
            "SELECT nome, preco, quantidade FROM produtos WHERE id = ?",
            (produto_id,)
        )
        produto = cursor.fetchone()

        if produto is None:
            conexao.close()
            return "Produto não encontrado."

        nome, preco, estoque = produto

        if quantidade > estoque:
            conexao.close()
            return "Estoque insuficiente!"

        total = preco * quantidade

        cursor.execute("""
            INSERT INTO vendas
            (produto_id, quantidade, valor_total, data_venda)
            VALUES (?, ?, ?, ?)
        """, (produto_id, quantidade, total, datetime.now().isoformat()))

        cursor.execute(
            "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
            (quantidade, produto_id)
        )

        conexao.commit()
        conexao.close()

        return f"""
    <style>
        body {{
            font-family: Arial;
            background: #faf5ed;
            color: #493323;
            padding: 30px;
        }}

        .card {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 500px;
        }}

        h1 {{
            color: #70452f;
        }}

        a {{
            display: inline-block;
            color: white;
            background: #a95f35;
            padding: 10px 15px;
            margin: 8px 5px 0 0;
            border-radius: 6px;
            text-decoration: none;
        }}
    </style>

    <div class="card">
        <h1>✓ Venda realizada com sucesso!</h1>
        <p>Produto: {nome}</p>
        <p>Quantidade: {quantidade}</p>
        <p>Total: R$ {total:.2f}</p>

        <a href="/vendas">Nova venda</a>
        <a href="/produtos">Consultar estoque</a>
        <a href="/historico">Histórico de vendas</a>
        <a href="/">Início</a>
    </div>
        """

    cursor.execute("SELECT id, nome, preco, quantidade FROM produtos")
    lista = cursor.fetchall()
    conexao.close()

    return render_template_string("""
    <style>
        body {
            font-family: Arial;
            background: #faf5ed;
            color: #493323;
            padding: 30px;
        }

        h1 {
            color: #70452f;
        }

        form {
            background: white;
            padding: 25px;
            border-radius: 12px;
            max-width: 450px;
        }

        input, select, button {
            padding: 12px;
            margin: 8px 0;
            width: 100%;
            box-sizing: border-box;
        }

        button {
            background: #a95f35;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }

        a {
            color: #70452f;
        }
    </style>

    <h1>🛒 Registrar Venda</h1>

    <form method="POST">
        <label>Produto:</label>

        <select name="produto_id" required>
            {% for produto in lista %}
                <option value="{{ produto[0] }}">
                    {{ produto[1] }} - R$ {{ "%.2f"|format(produto[2]) }}
                    (Estoque: {{ produto[3] }})
                </option>
            {% endfor %}
        </select>

        <label>Quantidade:</label>
        <input type="number" name="quantidade" min="1" required>

        <button type="submit">Finalizar venda</button>
    </form>

    <br>
    <a href="/">Voltar ao início</a>

""", lista=lista)


@app.route("/historico")
def historico():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT vendas.id, produtos.nome,
               vendas.quantidade, vendas.valor_total,
               vendas.data_venda
        FROM vendas
        JOIN produtos ON vendas.produto_id = produtos.id
        ORDER BY vendas.id DESC
    """)

    lista = cursor.fetchall()
    conexao.close()

    return render_template_string("""
    <style>
        body {
            font-family: Arial;
            background: #faf5ed;
            color: #493323;
            padding: 30px;
        }

        h1 {
            color: #70452f;
        }

        .venda {
            background: white;
            padding: 18px;
            margin-bottom: 15px;
            border-radius: 10px;
        }

        a {
            color: #70452f;
        }
    </style>

    <h1>📋 Histórico de Vendas</h1>

    {% for venda in lista %}
        <div class="venda">
            <strong>Venda nº {{ venda[0] }}</strong>
            <p>Produto: {{ venda[1] }}</p>
            <p>Quantidade: {{ venda[2] }}</p>
            <p>Total: R$ {{ "%.2f"|format(venda[3]) }}</p>
            <p>Data: {{ venda[4] }}</p>
        </div>
    {% else %}
        <p>Nenhuma venda registrada.</p>
    {% endfor %}

    <br>
    <a href="/">Voltar ao início</a>

""", lista=lista)


criar_tabela()

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))