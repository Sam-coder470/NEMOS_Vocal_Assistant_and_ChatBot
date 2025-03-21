import sqlite3

# Création de la base de données
def init_db():
    conn = sqlite3.connect("nemos.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        response TEXT
    )
    """)
    
    conn.commit()
    conn.close()

init_db()  # Crée la base de données au lancement

# Ajouter une fonction pour enregistrer une question-réponse
def save_to_db(question, response):
    conn = sqlite3.connect("nemos.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO conversations (question, response) VALUES (?, ?)", (question, response))
        conn.commit()
    except sqlite3.IntegrityError:
        print("🔹 La question est déjà enregistrée.")
    
    conn.close()

# Vérifier si une réponse existe avant d’appeler Hugging Face (sans matching approximatif)
def get_from_db(question):
    conn = sqlite3.connect("nemos.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT response FROM conversations WHERE question = ?", (question,))
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0] if result else None
