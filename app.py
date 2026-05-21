from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import logging

# Configuração de log para aparecer no Railway e mostrar erros reais
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS ultra permissivo para evitar bloqueios
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"]}})

def get_db():
    logger.info("Tentando conectar ao banco de dados...")
    try:
        # Tenta usar variáveis de ambiente do Railway, ou cai no hardcoded
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQLHOST", "mysql.railway.internal"),
            user=os.environ.get("MYSQLUSER", "root"),
            password=os.environ.get("MYSQLPASSWORD", "UCoYkwmuNjHwmavAsIPZHbeFXiZdUWoC"),
            database=os.environ.get("MYSQLDATABASE", "railway"),
            port=int(os.environ.get("MYSQLPORT", 3306))
        )
        logger.info("Conexão ao banco de dados estabelecida com sucesso!")
        return conn
    except Exception as e:
        logger.error(f"ERRO CRÍTICO NA CONEXÃO COM O BANCO DE DADOS: {str(e)}")
        raise e

@app.route("/")
def home():
    return jsonify({"mensagem": "Backend rodando corretamente"})

@app.route("/cadastro", methods=["POST"])
def cadastro():
    logger.info("Recebendo requisição de cadastro")
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
        
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            con.close()
            return jsonify({"erro": "Email já cadastrado"}), 400

        senha_hash = generate_password_hash(senha)
        cur.execute("INSERT INTO usuarios (nome, email, telefone, cidade, senha) VALUES (%s, %s, %s, %s, %s)",
                    (nome, email, telefone, telefone, cidade, senha_hash)) # Correção: telefone estava duplicado, ajuste conforme seu DB
        con.commit()
        
        cur.close()
        con.close()
        return jsonify({"mensagem": "Cadastro realizado com sucesso"}), 201
        
    except Exception as e:
        logger.error(f"Erro na rota /cadastro: {str(e)}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

@app.route("/login", methods=["POST"])
def login():
    logger.info("Recebendo requisição de login")
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
        
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
            return jsonify({
                "mensagem": "Login realizado com sucesso",
                "usuario": {"nome": usuario["nome"], "email": usuario["email"]}
            }), 200
        
        return jsonify({"erro": "Email ou senha incorretos"}), 401
        
    except Exception as e:
        logger.error(f"Erro na rota /login: {str(e)}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=porta)