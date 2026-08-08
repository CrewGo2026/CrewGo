from database.db import get_connection


def crea_operaio(
    nome,
    cognome,
    email="",
    telefono="",
    mansione="",
    squadra_id=None,
    data_assunzione="",
    stato="Attivo"
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO operai (
            nome,
            cognome,
            email,
            telefono,
            mansione,
            squadra_id,
            data_assunzione,
            stato
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            cognome,
            email,
            telefono,
            mansione,
            squadra_id,
            data_assunzione,
            stato
        )
    )

    conn.commit()

    operaio_id = cursor.lastrowid

    conn.close()

    return operaio_id


def elenco_operai():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
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
        ORDER BY cognome, nome
        """
    )

    operai = [
        dict(riga)
        for riga in cursor.fetchall()
    ]

    conn.close()

    return operai


def trova_operaio(operaio_id):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
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
        WHERE id = ?
        """,
        (operaio_id,)
    )

    riga = cursor.fetchone()

    conn.close()

    if riga:
        return dict(riga)

    return None


def modifica_operaio(
    operaio_id,
    nome,
    cognome,
    email="",
    telefono="",
    mansione="",
    squadra_id=None,
    data_assunzione="",
    stato="Attivo"
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE operai
        SET
            nome = ?,
            cognome = ?,
            email = ?,
            telefono = ?,
            mansione = ?,
            squadra_id = ?,
            data_assunzione = ?,
            stato = ?
        WHERE id = ?
        """,
        (
            nome,
            cognome,
            email,
            telefono,
            mansione,
            squadra_id,
            data_assunzione,
            stato,
            operaio_id
        )
    )

    conn.commit()

    modificato = cursor.rowcount > 0

    conn.close()

    return modificato


def cambia_stato_operaio(operaio_id, stato):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE operai
        SET stato = ?
        WHERE id = ?
        """,
        (stato, operaio_id)
    )

    conn.commit()

    modificato = cursor.rowcount > 0

    conn.close()

    return modificato


def elimina_operaio(operaio_id):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM operai
        WHERE id = ?
        """,
        (operaio_id,)
    )

    conn.commit()

    eliminato = cursor.rowcount > 0

    conn.close()

    return eliminato