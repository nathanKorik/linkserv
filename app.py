from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host="mysql.railway.internal",
        user="root",
        password="UCoYkwmuNjHwmavAsIPZHbeFXiZdUWoC",
        database="railway",
        port=3306
    )

@app.route("/")
def home():
    return jsonify({"mensagem": "Backend funcionando"})

@app.route("/cadastro", methods=["POST"])
def cadastro():
    dados = request.json
    nome = dados.get("nome")
    email = dados.get("email")
    telefone = dados.get("telefone")
    cidade = dados.get("cidade")
    senha = dados.get("senha")
    confirmar_senha = dados.get("confirmar_senha")

    if not nome or not email or not telefone or not cidade or not senha or not confirmar_senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400
    if senha != confirmar_senha:
        return jsonify({"erro": "As senhas não são iguais"}), 400

    con = get_db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    if cur.fetchone():
        return jsonify({"erro": "Email já cadastrado"}), 400

    senha_criptografada = generate_password_hash(senha)
    cur.execute("INSERT INTO usuarios (nome, email, telefone, cidade, senha) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, telefone, cidade, senha_criptografada))
    con.commit()
    cur.close()
    con.close()
    return jsonify({"mensagem": "Cadastro realizado com sucesso"}), 201

@app.route("/login", methods=["POST"])
def login():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({"erro": "Preencha email e senha"}), 400

    con = get_db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()
    con.close()

    if usuario and check_password_hash(usuario["senha"], senha):
        return jsonify({
            "mensagem": "Login realizado com sucesso",
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "telefone": usuario["telefone"],
                "cidade": usuario["cidade"]
            }
        }), 200

    return jsonify({"erro": "Email ou senha incorretos"}), 401

if __name__ == "__main__":
    app.run(debug=True)