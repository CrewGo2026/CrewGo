from flask import Flask, send_from_directory, request, redirect, session, jsonify
from database.users import verifica_login
from database.db import inizializza_database
from database.operai import (
    crea_operaio,
    elenco_operai,
    trova_operaio,
    modifica_operaio,
    cambia_stato_operaio,
    elimina_operaio
)


app = Flask(__name__)

app.secret_key = "crewgo-chiave-temporanea"


inizializza_database()


def autenticato():
    return "utente" in session


@app.route("/")
def home():

    if autenticato():
        return redirect("/dashboard")

    return send_from_directory("../frontend", "login.html")


@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    user = verifica_login(email, password)

    if user:

        session["utente"] = user["nome"]
        session["ruolo"] = user["ruolo"]

        return redirect("/dashboard")

    return """
    <h2>Accesso non riuscito</h2>
    <p>Email o password non corretti.</p>
    <a href="/">Torna al login</a>
    """, 401


@app.route("/dashboard")
def dashboard():

    if not autenticato():
        return redirect("/")

    return send_from_directory("../frontend", "index.html")


@app.route("/operai")
def operai():

    if not autenticato():
        return redirect("/")

    return send_from_directory("../frontend", "operai.html")


@app.route("/cantieri")
def cantieri():

    if not autenticato():
        return redirect("/")

    return send_from_directory("../frontend", "cantieri.html")


@app.route("/squadre")
def squadre():

    if not autenticato():
        return redirect("/")

    return send_from_directory("../frontend", "squadre.html")


@app.route("/ore")
def ore():

    if not autenticato():
        return redirect("/")

    return send_from_directory("../frontend", "ore.html")


# ==========================================================
# API OPERAI
# ==========================================================

@app.route("/api/operai", methods=["GET"])
def api_elenco_operai():

    if not autenticato():
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    return jsonify(elenco_operai())


@app.route("/api/operai", methods=["POST"])
def api_crea_operaio():

    if not autenticato():
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    dati = request.get_json(silent=True) or {}

    nome = dati.get("nome", "").strip()
    cognome = dati.get("cognome", "").strip()

    if not nome or not cognome:
        return jsonify({
            "errore": "Nome e cognome sono obbligatori"
        }), 400

    operaio_id = crea_operaio(
        nome=nome,
        cognome=cognome,
        email=dati.get("email", "").strip(),
        telefono=dati.get("telefono", "").strip(),
        mansione=dati.get("mansione", "").strip(),
        squadra_id=dati.get("squadra_id"),
        data_assunzione=dati.get("data_assunzione", ""),
        stato=dati.get("stato", "Attivo")
    )

    return jsonify({
        "successo": True,
        "id": operaio_id
    }), 201


@app.route("/api/operai/<int:operaio_id>", methods=["GET"])
def api_trova_operaio(operaio_id):

    if not autenticato():
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    operaio = trova_operaio(operaio_id)

    if not operaio:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify(operaio)


@app.route("/api/operai/<int:operaio_id>", methods=["PUT"])
def api_modifica_operaio(operaio_id):

    if not autenticato():
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    dati = request.get_json(silent=True) or {}

    nome = dati.get("nome", "").strip()
    cognome = dati.get("cognome", "").strip()

    if not nome or not cognome:
        return jsonify({
            "errore": "Nome e cognome sono obbligatori"
        }), 400

    modificato = modifica_operaio(
        operaio_id=operaio_id,
        nome=nome,
        cognome=cognome,
        email=dati.get("email", "").strip(),
        telefono=dati.get("telefono", "").strip(),
        mansione=dati.get("mansione", "").strip(),
        squadra_id=dati.get("squadra_id"),
        data_assunzione=dati.get("data_assunzione", ""),
        stato=dati.get("stato", "Attivo")
    )

    if not modificato:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


@app.route("/api/operai/<int:operaio_id>/stato", methods=["PUT"])
def api_cambia_stato_operaio(operaio_id):

    if not autenticato():
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    dati = request.get_json(silent=True) or {}

    stato = dati.get("stato")

    if stato not in ["Attivo", "Non attivo"]:
        return jsonify({
            "errore": "Stato non valido"
        }), 400

    modificato = cambia_stato_operaio(
        operaio_id,
        stato
    )

    if not modificato:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


@app.route("/api/operai/<int:operaio_id>", methods=["DELETE"])
def api_elimina_operaio(operaio_id):

    if not autenticato():
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    eliminato = elimina_operaio(operaio_id)

    if not eliminato:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


# ==========================================================
# API UTENTE
# ==========================================================

@app.route("/api/utente")
def utente():

    if not autenticato():
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    return jsonify({
        "nome": session["utente"],
        "ruolo": session["ruolo"]
    })


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":

    app.run(debug=True)