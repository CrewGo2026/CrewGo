from flask import Flask, send_from_directory, request, redirect, session
from database.users import verifica_login

app = Flask(__name__)

app.secret_key = "crewgo-chiave-temporanea"


@app.route("/")
def home():
    if "utente" in session:
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
    if "utente" not in session:
        return redirect("/")

    return send_from_directory("../frontend", "index.html")


@app.route("/operai")
def operai():
    if "utente" not in session:
        return redirect("/")

    return send_from_directory("../frontend", "operai.html")


@app.route("/cantieri")
def cantieri():
    if "utente" not in session:
        return redirect("/")

    return send_from_directory("../frontend", "cantieri.html")


@app.route("/squadre")
def squadre():
    if "utente" not in session:
        return redirect("/")

    return send_from_directory("../frontend", "squadre.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/api/utente")
def utente():
    if "utente" not in session:
        return {"errore": "Non autenticato"}, 401

    return {
        "nome": session["utente"],
        "ruolo": session["ruolo"]
    }


if __name__ == "__main__":
    app.run(debug=True)