from flask import Blueprint, render_template, request, redirect, session
from models.consulta import Consulta
from models.paciente import Paciente
from models.medico import Medico
from extensions import db
from utils.email_service import enviar_email

consulta_bp = Blueprint("consulta", __name__)


# 📌 LISTAR CONSULTAS
@consulta_bp.route("/consultas")
def consultas():

    if not session.get("logado"):
        return redirect("/login")

    lista = Consulta.query.all()
    return render_template("consultas.html", lista=lista)


# 📌 AGENDAR CONSULTA
@consulta_bp.route("/agendar", methods=["GET", "POST"])
def agendar():

    if not session.get("logado"):
        return redirect("/login")

    pacientes = Paciente.query.all()
    medicos = Medico.query.all()

    if request.method == "POST":

        # 🚨 BLOQUEIO DE HORÁRIO (ESSENCIAL PARA NOTA)
        conflito = Consulta.query.filter_by(
            medico_id=request.form["medico_id"],
            data=request.form["data"],
            hora=request.form["hora"],
            status="Agendada"
        ).first()

        if conflito:
            return "❌ Horário já ocupado"

        consulta = Consulta(
            paciente_id=request.form["paciente_id"],
            medico_id=request.form["medico_id"],
            data=request.form["data"],
            hora=request.form["hora"],
            status="Agendada"
        )

        db.session.add(consulta)
        db.session.commit()

        # Envia email (falha silenciosa para não travar o agendamento)
        try:
            paciente = db.session.get(Paciente, int(request.form["paciente_id"]))
            medico   = db.session.get(Medico,   int(request.form["medico_id"]))

            if paciente and paciente.email:
                enviar_email(
                    paciente.email,
                    paciente.nome,
                    consulta.data,
                    consulta.hora,
                    medico.nome if medico else ""
                )
        except Exception as e:
            print("[EMAIL] Erro ao enviar email:", e)

        return redirect("/consultas")

    return render_template("agendar.html", pacientes=pacientes, medicos=medicos)


# 📌 CANCELAR CONSULTA
@consulta_bp.route("/cancelar/<int:id>")
def cancelar(id):

    consulta = db.session.get(Consulta, id)
    if consulta:
        consulta.status = "Cancelada"
        db.session.commit()

    return redirect("/consultas")


# 📌 REAGENDAR CONSULTA
@consulta_bp.route("/reagendar/<int:id>", methods=["GET", "POST"])
def reagendar(id):

    consulta = db.session.get(Consulta, id)

    if request.method == "POST":

        consulta.data = request.form["data"]
        consulta.hora = request.form["hora"]

        db.session.commit()

        return redirect("/consultas")

    return render_template("reagendar.html", consulta=consulta)