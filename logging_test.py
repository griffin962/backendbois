#!/usr/bin/env python3

import logging
import logging.handlers

from klap4 import db


def main():
    db.connect("test.db")

    logger = logging.getLogger("main")
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(db.DBHandler())
    logger.setLevel(logging.DEBUG)

    logger.debug("Looping")

    logger.critical("REALLY BAD")


if __name__ == '__main__':
    main()
