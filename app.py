import os
from flask import Flask, render_template, redirect, request, session
from extensions import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "123")

# 📌 Banco de dados
# Em produção usa DATABASE_URL (Railway/PostgreSQL), localmente usa SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 📌 IMPORTAÇÃO DOS MODELOS
from models.paciente import Paciente
from models.consulta import Consulta
from models.medico import Medico

# 📌 IMPORTAÇÃO DOS CONTROLLERS
from controllers.paciente_controller import paciente_bp
from controllers.consulta_controller import consulta_bp

app.register_blueprint(paciente_bp)
app.register_blueprint(consulta_bp)


# =========================
# 🔵 ROTAS PRINCIPAIS
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "admin" and senha == "123":
            session["logado"] = True
            return redirect("/menu")

    return render_template("login.html")


@app.route("/menu")
def menu():

    if not session.get("logado"):
        return redirect("/login")

    return render_template("menu.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# 🧠 CRIAÇÃO DO BANCO + DADOS INICIAIS (SEED)
# =========================

with app.app_context():

    db.create_all()

    # 🔥 INSERIR MÉDICOS AUTOMATICAMENTE (SÓ 1 VEZ)
    if Medico.query.count() == 0:

        medico1 = Medico(
            nome="Dr. João Antônio",
            especialidade="Cardiologia"
        )

        medico2 = Medico(
            nome="Dra Maria Aparecida",
            especialidade="Dermatologia"
        )

        medico3 = Medico(
            nome="Dr. João da Silva",
            especialidade="Clínica Geral"
        )

        db.session.add_all([medico1, medico2, medico3])
        db.session.commit()

        print("✔ Médicos cadastrados com sucesso!")


# =========================
# 🚀 EXECUÇÃO
# =========================

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
