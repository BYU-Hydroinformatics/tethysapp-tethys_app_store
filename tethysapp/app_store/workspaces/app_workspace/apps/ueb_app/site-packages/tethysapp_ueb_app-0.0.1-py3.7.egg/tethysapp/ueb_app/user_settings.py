from .app import UebApp as app

hs_name = app.get_custom_setting('hs_name')
hs_password = app.get_custom_setting('hs_password')
hydrods_name = app.get_custom_setting('hydrods_name')
hydrods_password = app.get_custom_setting('hydrods_password')
client_id = app.get_custom_setting('client_id')
client_secret = app.get_custom_setting('client_secret')