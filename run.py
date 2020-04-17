#!/usr/bin/env python3

import sys

from klap4 import api, db


def main():
    is_production = False
    if len(sys.argv) > 1 and sys.argv[1] == "--production":
        is_production = True

    db.connect("test.db", db_log_level="debug" if not is_production else "warning")
    api.app.run(debug=not is_production)  # TODO if in production use a professional webserver like Waitress.


if __name__ == '__main__':
    main()

