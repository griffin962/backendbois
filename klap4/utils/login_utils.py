from ldap3 import Server, Connection, ALL

def login(user):
    server = Server('ldap.kmnr.us', use_ssl=True, get_info=ALL)
    conn = Connection(server, 'uid=klap-test,ou=people,dc=kmnr,dc=us', 'g0Zn3ll', auto_bind=True)
    print(conn)