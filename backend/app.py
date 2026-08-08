from flask import Flask, send_from_directory, request, redirect, session, jsonify
from database.users import verifica_login
from database.db import inizializza_database, get_connection
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


# ==========================================================
# FUNZIONI GENERALI
# ==========================================================

def autenticato():
    return "utente" in session


def errore_non_autenticato():
    return jsonify({
        "errore": "Non autenticato"
    }), 401


def dati_json():
    return request.get_json(silent=True) or {}


# ==========================================================
# PAGINE
# ==========================================================

@app.route("/")
def home():

    if autenticato():
        return redirect("/dashboard")

    return send_from_directory("../frontend", "login.html")


@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

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
# API UTENTE
# ==========================================================

@app.route("/api/utente")
@app.route("/mezzi")
def mezzi():
    if not autenticato():
        return redirect("/")
    return send_from_directory("../frontend", "mezzi.html")

def api_utente():

    if not autenticato():
        return errore_non_autenticato()

    return jsonify({
        "nome": session["utente"],
        "ruolo": session["ruolo"]
    })


# ==========================================================
# API OPERAI
# ==========================================================

@app.route("/api/operai", methods=["GET"])
def api_elenco_operai():

    if not autenticato():
        return errore_non_autenticato()

    return jsonify(elenco_operai())


@app.route("/api/operai", methods=["POST"])
def api_crea_operaio():

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    nome = str(dati.get("nome", "")).strip()
    cognome = str(dati.get("cognome", "")).strip()

    if not nome or not cognome:
        return jsonify({
            "errore": "Nome e cognome sono obbligatori"
        }), 400

    squadra_id = dati.get("squadra_id")

    if squadra_id == "":
        squadra_id = None

    operaio_id = crea_operaio(
        nome=nome,
        cognome=cognome,
        email=str(dati.get("email", "")).strip(),
        telefono=str(dati.get("telefono", "")).strip(),
        mansione=str(dati.get("mansione", "")).strip(),
        squadra_id=squadra_id,
        data_assunzione=str(
            dati.get("data_assunzione", "")
        ),
        stato=str(
            dati.get("stato", "Attivo")
        )
    )

    return jsonify({
        "successo": True,
        "id": operaio_id
    }), 201


@app.route("/api/operai/<int:operaio_id>", methods=["GET"])
def api_trova_operaio(operaio_id):

    if not autenticato():
        return errore_non_autenticato()

    operaio = trova_operaio(operaio_id)

    if not operaio:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify(operaio)


@app.route("/api/operai/<int:operaio_id>", methods=["PUT"])
def api_modifica_operaio(operaio_id):

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    nome = str(dati.get("nome", "")).strip()
    cognome = str(dati.get("cognome", "")).strip()

    if not nome or not cognome:
        return jsonify({
            "errore": "Nome e cognome sono obbligatori"
        }), 400

    squadra_id = dati.get("squadra_id")

    if squadra_id == "":
        squadra_id = None

    modificato = modifica_operaio(
        operaio_id=operaio_id,
        nome=nome,
        cognome=cognome,
        email=str(dati.get("email", "")).strip(),
        telefono=str(dati.get("telefono", "")).strip(),
        mansione=str(dati.get("mansione", "")).strip(),
        squadra_id=squadra_id,
        data_assunzione=str(
            dati.get("data_assunzione", "")
        ),
        stato=str(
            dati.get("stato", "Attivo")
        )
    )

    if not modificato:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


@app.route("/api/operai/<int:operaio_id>/stato", methods=["PUT"])
def api_stato_operaio(operaio_id):

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

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
        return errore_non_autenticato()

    eliminato = elimina_operaio(operaio_id)

    if not eliminato:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


# ==========================================================
# API CANTIERI
# ==========================================================

@app.route("/api/cantieri", methods=["GET"])
def api_elenco_cantieri():

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            cliente,
            citta,
            indirizzo,
            data_inizio,
            data_fine,
            caposquadra,
            stato
        FROM cantieri
        ORDER BY id DESC
    """)

    risultati = [
        dict(riga)
        for riga in cursor.fetchall()
    ]

    conn.close()

    return jsonify(risultati)


@app.route("/api/cantieri", methods=["POST"])
def api_crea_cantiere():

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    nome = str(dati.get("nome", "")).strip()
    cliente = str(dati.get("cliente", "")).strip()
    citta = str(dati.get("citta", "")).strip()

    if not nome or not cliente or not citta:
        return jsonify({
            "errore": "Nome, cliente e città sono obbligatori"
        }), 400

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cantieri (
            nome,
            cliente,
            citta,
            indirizzo,
            data_inizio,
            data_fine,
            caposquadra,
            stato
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome,
        cliente,
        citta,
        str(dati.get("indirizzo", "")).strip(),
        str(dati.get("data_inizio", "")),
        str(dati.get("data_fine", "")),
        str(dati.get("caposquadra", "")).strip(),
        str(dati.get("stato", "Attivo"))
    ))

    conn.commit()

    cantiere_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "successo": True,
        "id": cantiere_id
    }), 201


@app.route("/api/cantieri/<int:cantiere_id>", methods=["PUT"])
def api_modifica_cantiere(cantiere_id):

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    nome = str(dati.get("nome", "")).strip()
    cliente = str(dati.get("cliente", "")).strip()
    citta = str(dati.get("citta", "")).strip()

    if not nome or not cliente or not citta:
        return jsonify({
            "errore": "Nome, cliente e città sono obbligatori"
        }), 400

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cantieri
        SET
            nome = ?,
            cliente = ?,
            citta = ?,
            indirizzo = ?,
            data_inizio = ?,
            data_fine = ?,
            caposquadra = ?,
            stato = ?
        WHERE id = ?
    """, (
        nome,
        cliente,
        citta,
        str(dati.get("indirizzo", "")).strip(),
        str(dati.get("data_inizio", "")),
        str(dati.get("data_fine", "")),
        str(dati.get("caposquadra", "")).strip(),
        str(dati.get("stato", "Attivo")),
        cantiere_id
    ))

    conn.commit()

    modificato = cursor.rowcount > 0

    conn.close()

    if not modificato:
        return jsonify({
            "errore": "Cantiere non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


@app.route("/api/cantieri/<int:cantiere_id>", methods=["DELETE"])
def api_elimina_cantiere(cantiere_id):

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM cantieri
        WHERE id = ?
    """, (cantiere_id,))

    conn.commit()

    eliminato = cursor.rowcount > 0

    conn.close()

    if not eliminato:
        return jsonify({
            "errore": "Cantiere non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


# ==========================================================
# API SQUADRE
# ==========================================================

@app.route("/api/squadre", methods=["GET"])
def api_elenco_squadre():

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.nome,
            s.caposquadra,
            s.cantiere_id,
            s.stato,
            c.nome AS cantiere_nome
        FROM squadre s
        LEFT JOIN cantieri c
            ON c.id = s.cantiere_id
        ORDER BY s.id DESC
    """)

    squadre = []

    for riga in cursor.fetchall():

        squadra = dict(riga)

        cursor.execute("""
            SELECT COUNT(*)
            FROM operai
            WHERE squadra_id = ?
        """, (squadra["id"],))

        squadra["numero_operai"] = cursor.fetchone()[0]

        squadre.append(squadra)

    conn.close()

    return jsonify(squadre)


@app.route("/api/squadre", methods=["POST"])
def api_crea_squadra():

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    nome = str(dati.get("nome", "")).strip()

    if not nome:
        return jsonify({
            "errore": "Il nome della squadra è obbligatorio"
        }), 400

    cantiere_id = dati.get("cantiere_id")

    if cantiere_id == "":
        cantiere_id = None

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO squadre (
            nome,
            caposquadra,
            cantiere_id,
            stato
        )
        VALUES (?, ?, ?, ?)
    """, (
        nome,
        str(dati.get("caposquadra", "")).strip(),
        cantiere_id,
        str(dati.get("stato", "Attiva"))
    ))

    conn.commit()

    squadra_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "successo": True,
        "id": squadra_id
    }), 201


@app.route("/api/squadre/<int:squadra_id>", methods=["PUT"])
def api_modifica_squadra(squadra_id):

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    nome = str(dati.get("nome", "")).strip()

    if not nome:
        return jsonify({
            "errore": "Il nome della squadra è obbligatorio"
        }), 400

    cantiere_id = dati.get("cantiere_id")

    if cantiere_id == "":
        cantiere_id = None

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE squadre
        SET
            nome = ?,
            caposquadra = ?,
            cantiere_id = ?,
            stato = ?
        WHERE id = ?
    """, (
        nome,
        str(dati.get("caposquadra", "")).strip(),
        cantiere_id,
        str(dati.get("stato", "Attiva")),
        squadra_id
    ))

    conn.commit()

    modificato = cursor.rowcount > 0

    conn.close()

    if not modificato:
        return jsonify({
            "errore": "Squadra non trovata"
        }), 404

    return jsonify({
        "successo": True
    })


@app.route("/api/squadre/<int:squadra_id>", methods=["DELETE"])
def api_elimina_squadra(squadra_id):

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE operai
        SET squadra_id = NULL
        WHERE squadra_id = ?
    """, (squadra_id,))

    cursor.execute("""
        DELETE FROM squadre
        WHERE id = ?
    """, (squadra_id,))

    conn.commit()

    eliminato = cursor.rowcount > 0

    conn.close()

    if not eliminato:
        return jsonify({
            "errore": "Squadra non trovata"
        }), 404

    return jsonify({
        "successo": True
    })


# ==========================================================
# API ASSEGNAZIONE OPERAI A SQUADRE
# ==========================================================

@app.route("/api/squadre/<int:squadra_id>/operai", methods=["GET"])
def api_operai_squadra(squadra_id):

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            cognome,
            email,
            telefono,
            mansione,
            squadra_id,
            data_assunzione,
            stato
        FROM operai
        WHERE squadra_id = ?
        ORDER BY cognome, nome
    """, (squadra_id,))

    risultati = [
        dict(riga)
        for riga in cursor.fetchall()
    ]

    conn.close()

    return jsonify(risultati)


@app.route("/api/squadre/<int:squadra_id>/operai", methods=["POST"])
def api_assegna_operaio_squadra(squadra_id):

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    operaio_id = dati.get("operaio_id")

    if not operaio_id:
        return jsonify({
            "errore": "Operaio obbligatorio"
        }), 400

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE operai
        SET squadra_id = ?
        WHERE id = ?
    """, (
        squadra_id,
        operaio_id
    ))

    conn.commit()

    modificato = cursor.rowcount > 0

    conn.close()

    if not modificato:
        return jsonify({
            "errore": "Operaio non trovato"
        }), 404

    return jsonify({
        "successo": True
    })


# ==========================================================
# API ORE LAVORATE
# ==========================================================

@app.route("/api/ore", methods=["GET"])
def api_elenco_ore():

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            o.id,
            o.data,
            o.operaio_id,
            o.squadra_id,
            o.cantiere_id,
            o.ore_ordinarie,
            o.ore_straordinarie,
            o.note,

            op.nome AS operaio_nome,
            op.cognome AS operaio_cognome,

            s.nome AS squadra_nome,

            c.nome AS cantiere_nome

        FROM ore o

        LEFT JOIN operai op
            ON op.id = o.operaio_id

        LEFT JOIN squadre s
            ON s.id = o.squadra_id

        LEFT JOIN cantieri c
            ON c.id = o.cantiere_id

        ORDER BY o.data DESC, o.id DESC
    """)

    risultati = [
        dict(riga)
        for riga in cursor.fetchall()
    ]

    conn.close()

    return jsonify(risultati)


@app.route("/api/ore", methods=["POST"])
def api_crea_ore():

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    data = str(dati.get("data", "")).strip()
    operaio_id = dati.get("operaio_id")
    squadra_id = dati.get("squadra_id")
    cantiere_id = dati.get("cantiere_id")

    if not data:
        return jsonify({
            "errore": "La data è obbligatoria"
        }), 400

    if not operaio_id:
        return jsonify({
            "errore": "L'operaio è obbligatorio"
        }), 400

    if not cantiere_id:
        return jsonify({
            "errore": "Il cantiere è obbligatorio"
        }), 400

    try:
        ore_ordinarie = float(
            dati.get("ore_ordinarie", 0)
        )

        ore_straordinarie = float(
            dati.get("ore_straordinarie", 0)
        )

    except (TypeError, ValueError):

        return jsonify({
            "errore": "Le ore devono essere numeri validi"
        }), 400

    if ore_ordinarie < 0 or ore_straordinarie < 0:

        return jsonify({
            "errore": "Le ore non possono essere negative"
        }), 400

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ore (
            data,
            operaio_id,
            squadra_id,
            cantiere_id,
            ore_ordinarie,
            ore_straordinarie,
            note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data,
        operaio_id,
        squadra_id,
        cantiere_id,
        ore_ordinarie,
        ore_straordinarie,
        str(dati.get("note", "")).strip()
    ))

    conn.commit()

    ore_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "successo": True,
        "id": ore_id
    }), 201


@app.route("/api/ore/<int:ore_id>", methods=["PUT"])
def api_modifica_ore(ore_id):

    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()

    try:

        ore_ordinarie = float(
            dati.get("ore_ordinarie", 0)
        )

        ore_straordinarie = float(
            dati.get("ore_straordinarie", 0)
        )

    except (TypeError, ValueError):

        return jsonify({
            "errore": "Le ore devono essere numeri validi"
        }), 400

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ore
        SET
            data = ?,
            operaio_id = ?,
            squadra_id = ?,
            cantiere_id = ?,
            ore_ordinarie = ?,
            ore_straordinarie = ?,
            note = ?
        WHERE id = ?
    """, (
        str(dati.get("data", "")),
        dati.get("operaio_id"),
        dati.get("squadra_id"),
        dati.get("cantiere_id"),
        ore_ordinarie,
        ore_straordinarie,
        str(dati.get("note", "")).strip(),
        ore_id
    ))

    conn.commit()

    modificato = cursor.rowcount > 0

    conn.close()

    if not modificato:
        return jsonify({
            "errore": "Registrazione ore non trovata"
        }), 404

    return jsonify({
        "successo": True
    })


@app.route("/api/ore/<int:ore_id>", methods=["DELETE"])
def api_elimina_ore(ore_id):

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM ore
        WHERE id = ?
    """, (ore_id,))

    conn.commit()

    eliminato = cursor.rowcount > 0

    conn.close()

    if not eliminato:
        return jsonify({
            "errore": "Registrazione ore non trovata"
        }), 404

    return jsonify({
        "successo": True
    })


# ==========================================================
# API DATI PER MENU E COLLEGAMENTI
# ==========================================================

@app.route("/api/dati-collegamento")
def api_dati_collegamento():

    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            cognome,
            stato
        FROM operai
        ORDER BY cognome, nome
    """)

    operai = [
        dict(riga)
        for riga in cursor.fetchall()
    ]


    cursor.execute("""
        SELECT
            id,
            nome,
            cliente,
            stato
        FROM cantieri
        ORDER BY nome
    """)

    cantieri = [
        dict(riga)
        for riga in cursor.fetchall()
    ]


    cursor.execute("""
        SELECT
            s.id,
            s.nome,
            s.cantiere_id,
            s.stato,
            c.nome AS cantiere_nome
        FROM squadre s
        LEFT JOIN cantieri c
            ON c.id = s.cantiere_id
        ORDER BY s.nome
    """)

    squadre = [
        dict(riga)
        for riga in cursor.fetchall()
    ]


    conn.close()


    return jsonify({
        "operai": operai,
        "cantieri": cantieri,
        "squadre": squadre
    })


# ==========================================================
# ==========================================================
# API MEZZI E ATTREZZATURE
# ==========================================================

@app.route("/api/mezzi", methods=["GET"])
def api_elenco_mezzi():
    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            m.id,
            m.nome,
            m.categoria,
            m.marca,
            m.modello,
            m.targa,
            m.matricola,
            m.stato,
            m.cantiere_id,
            m.squadra_id,
            m.note,
            c.nome AS cantiere_nome,
            s.nome AS squadra_nome
        FROM mezzi m
        LEFT JOIN cantieri c ON c.id = m.cantiere_id
        LEFT JOIN squadre s ON s.id = m.squadra_id
        ORDER BY m.id DESC
    """)

    risultati = [dict(riga) for riga in cursor.fetchall()]
    conn.close()
    return jsonify(risultati)


@app.route("/api/mezzi", methods=["POST"])
def api_crea_mezzo():
    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()
    nome = str(dati.get("nome", "")).strip()

    if not nome:
        return jsonify({"errore": "Il nome del mezzo è obbligatorio"}), 400

    cantiere_id = dati.get("cantiere_id") or None
    squadra_id = dati.get("squadra_id") or None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mezzi (
            nome, categoria, marca, modello, targa, matricola,
            stato, cantiere_id, squadra_id, note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome,
        str(dati.get("categoria", "Mezzo")).strip(),
        str(dati.get("marca", "")).strip(),
        str(dati.get("modello", "")).strip(),
        str(dati.get("targa", "")).strip(),
        str(dati.get("matricola", "")).strip(),
        str(dati.get("stato", "Disponibile")).strip(),
        cantiere_id,
        squadra_id,
        str(dati.get("note", "")).strip()
    ))

    conn.commit()
    mezzo_id = cursor.lastrowid
    conn.close()

    return jsonify({"successo": True, "id": mezzo_id}), 201


@app.route("/api/mezzi/<int:mezzo_id>", methods=["PUT"])
def api_modifica_mezzo(mezzo_id):
    if not autenticato():
        return errore_non_autenticato()

    dati = dati_json()
    nome = str(dati.get("nome", "")).strip()

    if not nome:
        return jsonify({"errore": "Il nome del mezzo è obbligatorio"}), 400

    cantiere_id = dati.get("cantiere_id") or None
    squadra_id = dati.get("squadra_id") or None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE mezzi
        SET
            nome = ?,
            categoria = ?,
            marca = ?,
            modello = ?,
            targa = ?,
            matricola = ?,
            stato = ?,
            cantiere_id = ?,
            squadra_id = ?,
            note = ?
        WHERE id = ?
    """, (
        nome,
        str(dati.get("categoria", "Mezzo")).strip(),
        str(dati.get("marca", "")).strip(),
        str(dati.get("modello", "")).strip(),
        str(dati.get("targa", "")).strip(),
        str(dati.get("matricola", "")).strip(),
        str(dati.get("stato", "Disponibile")).strip(),
        cantiere_id,
        squadra_id,
        str(dati.get("note", "")).strip(),
        mezzo_id
    ))

    conn.commit()
    modificato = cursor.rowcount > 0
    conn.close()

    if not modificato:
        return jsonify({"errore": "Mezzo non trovato"}), 404

    return jsonify({"successo": True})


@app.route("/api/mezzi/<int:mezzo_id>", methods=["DELETE"])
def api_elimina_mezzo(mezzo_id):
    if not autenticato():
        return errore_non_autenticato()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM mezzi WHERE id = ?", (mezzo_id,))
    conn.commit()
    eliminato = cursor.rowcount > 0
    conn.close()

    if not eliminato:
        return jsonify({"errore": "Mezzo non trovato"}), 404

    return jsonify({"successo": True})

# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================================================
# AVVIO
# ==========================================================

if __name__ == "__main__":

    app.run(debug=True)