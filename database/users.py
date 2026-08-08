from werkzeug.security import generate_password_hash, check_password_hash

users = {
    "titolare@crewgo.it": {
        "nome": "Titolare",
        "ruolo": "titolare",
        "password": generate_password_hash("CAMBIARE_PASSWORD")
    }
}


def verifica_login(email, password):
    user = users.get(email)

    if user and check_password_hash(user["password"], password):
        return user

    return None