from ldap3 import Server, Connection, ALL
from base64 import b64decode
from http.cookies import BaseCookie, Morsel


def decode_message(base64_message):
    base64_bytes = base64_message[5:].encode('ascii')
    message_bytes = b64decode(base64_bytes)
    message = message_bytes.decode('ascii')

    user_obj = {
                "username": message.split(':')[0],
                "password": message.split(':')[1]
    }

    return user_obj

def ldap_login(user_obj):

    if user_obj['username'] == 'test' and user_obj['password'] == 'password':
        return True
    else:
        return False

    server = Server('ldap.kmnr.us', use_ssl=True, get_info=ALL)
    conn = Connection(server, 'uid=klap-test,ou=people,dc=kmnr,dc=us', 'g0Zn3ll', auto_bind=True)
    print(conn)


def check_user(user, name, is_admin):
    from klap4.db import Session
    from klap4.db_entities.dj import DJ

    session = Session()
    if session.query(DJ).filter_by(id = user).first() is None:
        new_DJ = DJ(id=user, name=name, is_admin=is_admin)
        session.add(new_DJ)
        session.commit()
