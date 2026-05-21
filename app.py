from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import mysql.connector

app = Flask(__name__)
CORS(app)

# Função simplificada: Conecta apenas na hora da requisição
def get_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE"),
        port=int(os.environ.get("MYSQLPORT", 3306))
    )

@app.route("/", methods=["GET"])
def home():
    # Tenta conectar apenas ao receber um pedido
    try:
        conn = get_db()
        conn.close()
        return jsonify({"status": "Servidor e Banco de Dados OK!"})
    except Exception as e:
        return jsonify({"status": "Erro de conexão", "detalhe": str(e)}), 500

# Adicione suas rotas /login e /cadastro aqui...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)