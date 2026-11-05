from flask import Flask, request, redirect, render_template_string
from database import criar_tabela, conectar

app = Flask(__name__)

@app.route("/")
def inicio():
    return """
    <h1>🥖 Padaria Pão Quentinho</h1>
    <h2>Sistema de Estoque e Vendas</h2>
    <a href="/produtos">Cadastrar e consultar produtos</a>
    """

@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])
        quantidade = int(request.form["quantidade"])

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
            (nome, preco, quantidade)
        )

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
            <p>Nome do produto:</p>
            <input name="nome" required>

            <p>Preço:</p>
            <input name="preco" type="number"
                   step="0.01" min="0" required>

            <p>Quantidade em estoque:</p>
            <input name="quantidade" type="number"
                   min="0" required>

            <br><br>
            <button type="submit">Cadastrar produto</button>
        </form>

        <h2>Produtos cadastrados</h2>

        {% for produto in lista %}
            <p>
                {{ produto[1] }} -
                R$ {{ "%.2f"|format(produto[2]) }} -
                Estoque: {{ produto[3] }}
            </p>
        {% endfor %}

        <a href="/">Voltar ao início</a>
    """, lista=lista)


if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)