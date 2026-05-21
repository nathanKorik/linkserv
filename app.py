from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__)
# Habilita CORS para todas as origens e métodos
CORS(app, resources={r"/*": {"origins": "*"}})

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
    return jsonify({"mensagem": "Backend rodando corretamente"})

@app.route("/cadastro", methods=["POST"])
def cadastro():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
        
    nome = dados.get("nome")
    email = dados.get("email")
    telefone = dados.get("telefone")
    cidade = dados.get("cidade")
    senha = dados.get("senha")
    confirmar_senha = dados.get("confirmar_senha")

    if not all([nome, email, telefone, cidade, senha, confirmar_senha]):
        return jsonify({"erro": "Preencha todos os campos"}), 400
    
    if senha != confirmar_senha:
        return jsonify({"erro": "As senhas não são iguais"}), 400

    try:
        con = get_db()
        cur = con.cursor(dictionary=True)
        
        # Verifica se email já existe
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            con.close()
            return jsonify({"erro": "Email já cadastrado"}), 400

        # Insere novo usuario
        senha_hash = generate_password_hash(senha)
        cur.execute("INSERT INTO usuarios (nome, email, telefone, cidade, senha) VALUES (%s, %s, %s, %s, %s)",
                    (nome, email, telefone, cidade, senha_hash))
        con.commit()
        
        cur.close()
        con.close()
        return jsonify({"mensagem": "Cadastro realizado com sucesso"}), 201
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
        
    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({"erro": "Preencha email e senha"}), 400

    try:
        con = get_db()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close()
        con.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            return jsonify({
                "mensagem": "Login realizado com sucesso",
                "usuario": {"nome": usuario["nome"], "email": usuario["email"]}
            }), 200
        
        return jsonify({"erro": "Email ou senha incorretos"}), 401
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    # Pega a porta do ambiente (Railway define isso) ou usa 8080
    porta = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=porta)