from flask import Flask, request, render_template, redirect, session
import sqlite3
import os




app = Flask(__name__ , static_folder="static")
app.secret_key = "chave_insegura"  # inseguro: chave fixa
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Banco inicial (inseguro, sem hashing de senha)
def init_db():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, content TEXT)")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()
        # insere usuário no banco
        c.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
        conn.commit()

        # pega o id do usuário recém-criado
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        conn.close()

        # cria sessão
        session["user_id"] = user[0]
        session["username"] = username

        return redirect("/products")
    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = username
            return redirect("/products")
    return render_template("login.html")


@app.route("/products")
def products():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price, description, image FROM products")
    products = c.fetchall()
    conn.close()
    return render_template("products.html", products=products)


@app.route("/reviews", methods=["GET","POST"])
def reviews():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()
    if request.method == "POST":
        content = request.form["content"]  # inseguro: sem sanitização → XSS
        c.execute("INSERT INTO reviews (content) VALUES (?)", (content,))
        conn.commit()
    c.execute("SELECT * FROM reviews")
    all_reviews = c.fetchall()
    conn.close()
    return render_template("reviews.html", reviews=all_reviews)


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    return render_template("cart.html", cart=cart_items)


#@app.route("/checkout", methods=["GET","POST"])
#def checkout():
   # if request.method == "POST":
    #    card_number = request.form["card_number"]  # inseguro: dados sensíveis em texto puro
    ##   return f"Pagamento processado para {name} com cartão {card_number} (inseguro!)"
   # return render_template("checkout.html")



from datetime import datetime
from flask import render_template, request

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Exemplo: recupere os itens do carrinho (ajuste conforme sua lógica)
    # cart = get_cart_items()  # -> [{'id':1,'name':'Olaf','price':99.9,'quantity':1}, ...]
    cart = session.get('cart', [])  # exemplo simples; ajuste conforme seu app

    # Calcule contagem e total de forma defensiva
    cart_items_count = 0
    cart_total = 0.0
    for item in cart:
        # suporte tanto dicionários quanto tuplas: tente acessar por chave, senão por índice
        try:
            price = float(item.get('price', 0))
            qty = int(item.get('quantity', 1))
        except AttributeError:
            # item pode ser tupla: (id, name, price, quantity, image)
            price = float(item[2]) if len(item) > 2 else 0.0
            qty = int(item[3]) if len(item) > 3 else 1

        cart_items_count += qty
        cart_total += price * qty

    # Defina frete (float) — ajuste sua lógica de frete
    shipping = 0.0

    # Em POST, trate pagamento aqui (valide no servidor)
    if request.method == 'POST':
        # processar pagamento...
        pass

    return render_template(
        "checkout.html",
        cart_items_count=cart_items_count,
        cart_total=cart_total,
        shipping=shipping,
        current_year=datetime.utcnow().year
    )



@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        # inseguro: aceita qualquer tipo de arquivo
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return f"Arquivo {filename} enviado com sucesso (inseguro!)"
    return render_template("upload.html")



def init_db():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    # Tabela de usuários
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Tabela de produtos
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            description TEXT,
            image TEXT
        )
    """)

    # Tabela de reviews
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT
        )
    """)

    # Inserindo produtos iniciais se a tabela estiver vazia
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        produtos = [
            ("Boneco Olaf", 99.90, "Boneco de pelúcia do Olaf", "olaf.jpg"),
            ("Caneca Frozen", 39.90, "Caneca temática Frozen com Elsa e Anna", "caneca.jpg"),
            ("Camiseta Elsa", 59.90, "Camiseta estampada da Elsa", "camiseta.jpg"),
            ("Poster Frozen", 19.90, "Poster decorativo do filme Frozen", "poster.jpg"),
            ("Chaveiro Olaf", 14.90, "Chaveiro divertido do Olaf", "chaveiro.jpg"),
            ("Mochila Frozen", 129.90, "Mochila escolar temática Frozen", "mochila.jpg"),
            ("Boneca Elza", 129.90, "Boneca escolar temática Frozen", "Boneca.jpg")
        ]
        c.executemany(
            "INSERT INTO products (name, price, description, image) VALUES (?,?,?,?)",
            produtos
        )

    # Inserindo reviews iniciais se a tabela estiver vazia
    c.execute("SELECT COUNT(*) FROM reviews")
    if c.fetchone()[0] == 0:
        reviews_iniciais = [
            ("Loja incrível, produtos de ótima qualidade!"),
            ("Entrega rápida e atendimento excelente."),
            ("Adorei meu boneco Olaf, recomendo!")
        ]
        c.executemany("INSERT INTO reviews (content) VALUES (?)", [(r,) for r in reviews_iniciais])

    # Garante que o admin exista SEM atrapalhar outros usuários
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", ("admin", "admin123"))

    conn.commit()
    conn.close()





@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    quantity = int(request.form.get("quantity", 1))

    conn = sqlite3.connect("store.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price FROM products WHERE id=?", (product_id,))
    product = c.fetchone()
    conn.close()

    if product:
        # inicializa carrinho se não existir
        cart = session.get("cart", [])

        # procura se já existe o produto no carrinho
        for item in cart:
            if item["id"] == product[0]:
                item["quantity"] += quantity
                break
        else:
            # se não encontrou, adiciona novo item
            cart.append({
                "id": product[0],
                "name": product[1],
                "price": product[2],
                "quantity": quantity
            })

        # salva carrinho atualizado na sessão
        session["cart"] = cart

    return redirect("/cart")


@app.route("/logout")
def logout():
    # limpa todos os dados da sessão
    session.clear()
    # redireciona para a página inicial
    return redirect("/")




@app.route("/admin", methods=["GET","POST"])
def admin_panel():
    if "username" not in session or session["username"] != "admin":
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]
        image = request.form["image"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, description, image) VALUES (?,?,?,?)",
                  (name, price, description, image))
        conn.commit()
        conn.close()

        return redirect("/products")

    return render_template("admin.html")



@app.route("/search")
def search():
    term = request.args.get("q", "")
    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    # INSEGURO: concatenação direta → vulnerável a SQL Injection
    query = f"SELECT id, name, price, description, image FROM products WHERE name LIKE '%{term}%'"
    c.execute(query)
    results = c.fetchall()
    conn.close()

    return render_template("search.html", products=results)



from flask import redirect, url_for, session

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    # Recupera o carrinho da sessão
    cart = session.get('cart', [])

    # Filtra os itens, removendo o que tem o id correspondente
    cart = [item for item in cart if item['id'] != product_id]

    # Atualiza a sessão
    session['cart'] = cart

    # Redireciona de volta para a página do carrinho
    return redirect(url_for('cart'))




if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    init_db()
    #app.run(debug=True)  # inseguro: debug mode ativo
    app.run(host='0.0.0.0', port=5000)
