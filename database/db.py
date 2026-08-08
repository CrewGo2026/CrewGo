import sqlite3
from pathlib import Path


# ==========================================================
# PERCORSO DATABASE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "crewgo.db"


# ==========================================================
# CONNESSIONE
# ==========================================================

def get_connection():

    """
    Apre una connessione al database CrewGo.
    """

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================================
# INIZIALIZZAZIONE DATABASE
# ==========================================================

def inizializza_database():

    """
    Crea tutte le tabelle necessarie a CrewGo
    e aggiorna automaticamente la struttura
    delle tabelle già esistenti.
    """

    conn = get_connection()

    cursor = conn.cursor()


    # ======================================================
    # UTENTI
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            ruolo TEXT NOT NULL,
            password TEXT NOT NULL,
            attivo INTEGER DEFAULT 1
        )
    """)


    # ======================================================
    # OPERAI
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operai (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            mansione TEXT,
            squadra_id INTEGER,
            data_assunzione TEXT,
            stato TEXT DEFAULT 'Attivo',
            FOREIGN KEY (squadra_id)
                REFERENCES squadre(id)
        )
    """)


    # ======================================================
    # CANTIERI
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cantieri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cliente TEXT NOT NULL,
            citta TEXT NOT NULL,
            indirizzo TEXT,
            data_inizio TEXT,
            data_fine TEXT,
            caposquadra TEXT,
            stato TEXT DEFAULT 'Attivo'
        )
    """)


    # ======================================================
    # SQUADRE
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS squadre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            caposquadra TEXT,
            caposquadra_id INTEGER,
            cantiere_id INTEGER,
            stato TEXT DEFAULT 'Attiva',
            FOREIGN KEY (caposquadra_id)
                REFERENCES operai(id),
            FOREIGN KEY (cantiere_id)
                REFERENCES cantieri(id)
        )
    """)


    # ======================================================
    # ORE LAVORATE
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ore (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            operaio_id INTEGER,
            squadra_id INTEGER,
            cantiere_id INTEGER,
            ore_ordinarie REAL DEFAULT 0,
            ore_straordinarie REAL DEFAULT 0,
            note TEXT,
            FOREIGN KEY (operaio_id)
                REFERENCES operai(id),
            FOREIGN KEY (squadra_id)
                REFERENCES squadre(id),
            FOREIGN KEY (cantiere_id)
                REFERENCES cantieri(id)
        )
    """)


    # ======================================================
    # MIGRAZIONE SQUADRE ESISTENTI
    # ======================================================

    # Controlliamo se la vecchia tabella squadre
    # possiede già caposquadra_id.

    cursor.execute("""
        PRAGMA table_info(squadre)
    """)

    colonne_squadre = [
        riga["name"]
        for riga in cursor.fetchall()
    ]


    # Se il database esisteva già dalla versione precedente,
    # aggiungiamo la nuova colonna senza cancellare i dati.

    if "caposquadra_id" not in colonne_squadre:

        cursor.execute("""
            ALTER TABLE squadre
            ADD COLUMN caposquadra_id INTEGER
        """)


    # ======================================================
    # RECUPERO VECCHI CAPISQUADRA
    # ======================================================

    # Se avevamo già scritto un nome nel vecchio campo
    # "caposquadra", proviamo automaticamente a trovare
    # l'operaio corrispondente.

    cursor.execute("""
        SELECT
            id,
            caposquadra
        FROM squadre
        WHERE
            caposquadra IS NOT NULL
            AND TRIM(caposquadra) != ''
            AND (
                caposquadra_id IS NULL
                OR caposquadra_id = 0
            )
    """)

    vecchie_squadre = cursor.fetchall()


    for squadra in vecchie_squadre:

        nome_caposquadra = (
            squadra["caposquadra"]
            or ""
        ).strip()


        if not nome_caposquadra:
            continue


        # Prima proviamo "Nome Cognome"

        parti = nome_caposquadra.split()


        if len(parti) >= 2:

            nome = parti[0]

            cognome = " ".join(
                parti[1:]
            )


            cursor.execute("""
                SELECT id
                FROM operai
                WHERE
                    LOWER(nome) = LOWER(?)
                    AND LOWER(cognome) = LOWER(?)
                LIMIT 1
            """, (
                nome,
                cognome
            ))


            operaio = cursor.fetchone()


            if operaio:

                cursor.execute("""
                    UPDATE squadre
                    SET caposquadra_id = ?
                    WHERE id = ?
                """, (
                    operaio["id"],
                    squadra["id"]
                ))


    # ======================================================
    # COMMIT
    # ======================================================

    conn.commit()

    conn.close()


# ==========================================================
# AVVIO DIRETTO DEL FILE
# ==========================================================

if __name__ == "__main__":

    inizializza_database()

    print(
        "Database CrewGo inizializzato correttamente."
    )