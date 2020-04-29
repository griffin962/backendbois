from datetime import timedelta

def config():
    return {
        "clientOrigin": "http://localhost:8080",
        "accessExpiration": timedelta(hours=6),
        "refreshExpiration": timedelta(hours=6)
        }
        