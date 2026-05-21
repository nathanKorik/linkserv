from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import logging
import traceback

# Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# CORS liberado para qualquer origem
CORS(app)

def get_db():
    try:
        # Pega as variáveis do Railway configuradas por referência
        return mysql.connector.connect(
            host=os.environ.get("MYSQLHOST"),
            user=os.environ.get("MYSQLUSER"),
            password=os.environ.get("MYSQLPASSWORD"),
            database=os.environ.get("MYSQLDATABASE"),
            port=int(os.environ.get("MYSQLPORT", 3306))
        )
    except Exception as e:
        # Se falhar, imprime o erro detalhado no log do Railway
        logger.error(f"ERRO DE CONEXÃO AO BANCO: {traceback.format_exc()}")
        raise e

@app.route("/")
def home():
    return jsonify({"mensagem": "API Funcionando!"})

@app.route("/cadastro", methods=["POST"])
def cadastro():
    try:
        dados = request.get_json()
        nome = dados.get("nome")
        email = dados.get("email")
        telefone = dados.get("telefone")
        cidade = dados.get("cidade")
        senha = dados.get("senha")
        confirmar_senha = dados.get("confirmar_senha")

        if not all([nome, email, telefone, cidade, senha, confirmar_senha]):
            return jsonify({"erro": "Preencha todos os campos"}), 400
        
        if senha != confirmar_senha:
            return jsonify({"erro": "As senhas não coincidem"}), 400

        con = get_db()
        cur = con.cursor(dictionary=True)
        
        # Verifica se email existe
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            con.close()
            return jsonify({"erro": "Email já cadastrado"}), 400

        senha_hash = generate_password_hash(senha)
        cur.execute(
            "INSERT INTO usuarios (nome, email, telefone, cidade, senha) VALUES (%s, %s, %s, %s, %s)",
            (nome, email, telefone, cidade, senha_hash)
        )
        con.commit()
        
        cur.close()
        con.close()
        return jsonify({"mensagem": "Cadastro realizado com sucesso"}), 201
        
    except Exception:
        logger.error(f"Erro na rota /cadastro: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        dados = request.get_json()
        email = dados.get("email")
        senha = dados.get("senha")

        con = get_db()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close()
        con.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            return jsonify({"mensagem": "Login realizado com sucesso", "nome": usuario["nome"]}), 200
        
        return jsonify({"erro": "Email ou senha incorretos"}), 401
        
    except Exception:
        logger.error(f"Erro na rota /login: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)