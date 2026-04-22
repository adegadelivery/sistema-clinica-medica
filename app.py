import os
from flask import Flask, render_template, redirect, request, session, flash
from extensions import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "123")

# 📌 Banco de dados
# Em produção usa DATABASE_URL (Railway/PostgreSQL), localmente usa SQLite
# Se DATABASE_URL vier vazio ou ausente, usa SQLite como fallback
database_url = os.environ.get("DATABASE_URL", "").strip()
if not database_url:
    database_url = "sqlite:///db.sqlite3"
elif database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 📌 IMPORTAÇÃO DOS MODELOS
from models.paciente import Paciente
from models.consulta import Consulta
from models.medico import Medico
from models.usuario import Usuario

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

        usuario_form = request.form["usuario"]
        senha = request.form["senha"]

        # 🔑 Admin fixo (retrocompatibilidade)
        if usuario_form == "admin" and senha == "123":
            session["logado"] = True
            session["usuario_nome"] = "Administrador"
            return redirect("/menu")

        # 🔑 Usuários cadastrados no banco
        usuario_db = Usuario.query.filter_by(usuario=usuario_form).first()
        if usuario_db and usuario_db.verificar_senha(senha):
            session["logado"] = True
            session["usuario_nome"] = usuario_db.nome
            return redirect("/menu")

        flash("Usuário ou senha incorretos.", "danger")

    return render_template("login.html")


# =========================
# 📝 CADASTRO DE USUÁRIO
# =========================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        usuario_form = request.form["usuario"]
        senha = request.form["senha"]
        confirmar = request.form["confirmar"]

        # Validações
        if senha != confirmar:
            flash("As senhas não coincidem.", "danger")
            return render_template("cadastro.html")

        if Usuario.query.filter_by(usuario=usuario_form).first():
            flash("Nome de usuário já existe. Escolha outro.", "danger")
            return render_template("cadastro.html")

        if Usuario.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "danger")
            return render_template("cadastro.html")

        novo_usuario = Usuario(nome=nome, email=email, usuario=usuario_form)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect("/login")

    return render_template("cadastro.html")


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
