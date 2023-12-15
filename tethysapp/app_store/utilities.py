from cryptography.fernet import Fernet
from .app import AppStore as app

def encrypt(message: str, key: str) -> str:
    return (Fernet(key.encode()).encrypt(message.encode())).decode()

def decrypt(token: str, key: str) -> str:
    return (Fernet(key.encode()).decrypt(token.encode())).decode()


def get_available_stores_values(active_store):
    # breakpoint()
    available_stores_data_dict = app.get_custom_setting("stores_settings")['stores']
    if active_store != 'all':
        available_stores_data_dict = list(filter(lambda x: x['conda_channel'] == active_store, available_stores_data_dict))
    encryption_key = app.get_custom_setting("encryption_key")
    for store in available_stores_data_dict:
        store['github_token'] = decrypt(store['github_token'],encryption_key)
    return available_stores_data_dict