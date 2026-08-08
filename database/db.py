import sqlite3
from pathlib import Path


# Percorso del database
BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "crewgo.db"


def get_connection():
    """
    Apre una connessione al database CrewGo.
    """
    conn = sqlite3.connect(DATABASE_FILE)

    conn.row_factory = sqlite3.Row

    return conn


def inizializza_database():
    """
    Crea tutte le tabelle necessarie a CrewGo
    se non esistono già.
    """

    conn = get_connection()

    cursor = conn.cursor()


    # =========================
    # UTENTI
    # =========================

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


    # =========================
    # OPERAI
    # =========================

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


    # =========================
    # CANTIERI
    # =========================

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


    # =========================
    # SQUADRE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS squadre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            caposquadra TEXT,
            cantiere_id INTEGER,
            stato TEXT DEFAULT 'Attiva',
            FOREIGN KEY (cantiere_id)
                REFERENCES cantieri(id)
        )
    """)


    # =========================
    # ORE LAVORATE
    # =========================

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


    conn.commit()

    conn.close()


if __name__ == "__main__":
    inizializza_database()

    print("Database CrewGo inizializzato correttamente.")