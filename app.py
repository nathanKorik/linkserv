from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import logging

# Configuração de logs para que erros apareçam no log do Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração de CORS para permitir todas as origens
CORS(app)

def get_db():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQLHOST", "mysql.railway.internal"),
            user=os.environ.get("MYSQLUSER", "root"),
            password=os.environ.get("MYSQLPASSWORD", "UCoYkwmuNjHwmavAsIPZHbeFXiZdUWoC"),
            database=os.environ.get("MYSQLDATABASE", "railway"),
            port=int(os.environ.get("MYSQLPORT", 3306))
        )
        return conn
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {str(e)}")
        raise e

@app.route("/")
def home():
    return jsonify({"mensagem": "API Funcionando"})

@app.route("/cadastro", methods=["POST"])
def cadastro():
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

    try:
        con = get_db()
        cur = con.cursor(dictionary=True)
        
        # Verifica se email já existe
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            con.close()
            return jsonify({"erro": "Email já cadastrado"}), 400

        # Insere usuário (Corrigido para evitar erro de colunas)
        senha_hash = generate_password_hash(senha)
        cur.execute(
            "INSERT INTO usuarios (nome, email, telefone, cidade, senha) VALUES (%s, %s, %s, %s, %s)",
            (nome, email, telefone, cidade, senha_hash)
        )
        con.commit()
        
        cur.close()
        con.close()
        return jsonify({"mensagem": "Cadastro realizado"}), 201
        
    except Exception as e:
        logger.error(f"Erro no cadastro: {str(e)}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    email = dados.get("email")
    senha = dados.get("senha")

    try:
        con = get_db()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close()
        con.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            return jsonify({"mensagem": "Login ok", "nome": usuario["nome"]}), 200
        
        return jsonify({"erro": "Credenciais inválidas"}), 401
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)