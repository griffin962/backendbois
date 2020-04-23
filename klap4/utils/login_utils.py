from ldap3 import Server, Connection, ALL
from http.cookies import BaseCookie, Morsel

def login(user):
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
    
    user_obj = {
                'Set-Cookie': 'sid=123, userid=test, name=Test, role=admin'
    }
    return user_obj
