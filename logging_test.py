#!/usr/bin/env python3

from klap4 import db
from klap4.db_entities.software_log import SoftwareLog


def main():
    db.connect("test.db")

    session = db.Session()

    log = SoftwareLog("This is the first message test.")

    session.add(log)
    session.commit()


if __name__ == '__main__':
    main()
