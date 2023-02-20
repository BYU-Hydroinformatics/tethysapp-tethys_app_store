from cryptography.fernet import Fernet

def encrypt(message: str, key: str) -> str:
    return (Fernet(key.encode()).encrypt(message.encode())).decode()

def decrypt(token: str, key: str) -> str:
    return (Fernet(key.encode()).decrypt(token.encode())).decode()
