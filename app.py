from flask import Flask, request, redirect, render_template_string
from database import criar_tabela, conectar
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def inicio():
    return """
    <h1>🥖 Padaria Pão Quentinho</h1>
    <h2>Sistema de Estoque e Vendas</h2>
    <p><a href="/produtos">Cadastrar e consultar produtos</a></p>
    <p><a href="/vendas">Registrar venda</a></p>
    """

@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if request.method == "POST":
        nome = request.form["nome"]
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
        <h1>Cadastro de Produtos</h1>

        <form method="POST">
            <p>Nome:</p>
            <input name="nome" required>

            <p>Preço:</p>
            <input name="preco" type="number" step="0.01" min="0" required>

            <p>Quantidade:</p>
            <input name="quantidade" type="number" min="0" required>

            <p>Estoque mínimo:</p>
            <input name="estoque_minimo" type="number"
                   min="0" value="5" required>

            <br><br>
            <button type="submit">Cadastrar produto</button>
        </form>

        <h2>Estoque</h2>

        {% for produto in lista %}
            <p>
                {{ produto[1] }} -
                R$ {{ "%.2f"|format(produto[2]) }} -
                Quantidade: {{ produto[3] }}
                {% if produto[3] <= produto[4] %}
                    ⚠️ ESTOQUE BAIXO!
                {% endif %}
            </p>
        {% endfor %}

        <a href="/">Voltar</a>
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
            <h1>Venda realizada com sucesso!</h1>
            <p>Produto: {nome}</p>
            <p>Quantidade: {quantidade}</p>
            <p>Total: R$ {total:.2f}</p>
            <a href="/vendas">Nova venda</a>
            <br><a href="/produtos">Consultar estoque</a>
            <br><a href="/">Início</a>
        """

    cursor.execute("SELECT id, nome, preco, quantidade FROM produtos")
    lista = cursor.fetchall()
    conexao.close()

    return render_template_string("""
        <h1>Registrar Venda</h1>

        <form method="POST">
            <p>Produto:</p>
            <select name="produto_id" required>
                {% for produto in lista %}
                    <option value="{{ produto[0] }}">
                        {{ produto[1] }} - R$ {{ "%.2f"|format(produto[2]) }}
                        (Estoque: {{ produto[3] }})
                    </option>
                {% endfor %}
            </select>

            <p>Quantidade:</p>
            <input type="number" name="quantidade" min="1" required>

            <br><br>
            <button type="submit">Finalizar venda</button>
        </form>

        <a href="/">Voltar</a>
    """, lista=lista)


if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)