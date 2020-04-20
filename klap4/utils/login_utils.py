from ldap3 import Server, Connection, ALL

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
    
    user_obj = {"id": username, "name": name, "is_admin": is_admin}
    
    return user_obj
