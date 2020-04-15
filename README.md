# KMNR CTRL+F Backend
**CS 4096 SP2020 Senior Design**

Trello board can be found [here](https://trello.com/b/X7n73A1F/kmnr-ctrlf).


### Specifications:
- Python: `3.7`
- DBMS: `PostgreSQL`

### Steps to get set up
1. Clone this repo: `git clone https://github.com/vganesh1798/backendbois.git`
2. Make sure you have the python 3 `pipenv` package installed
3. run `pipenv shell` in the directory to set up pipenv and then run `pipenv install` to install all dependencies

### Running the Application
1. If pulling after updates, run `pipenv sync` to update package list, and then run `pipenv shell`
2. If it already exists in the project's root directory, delete the `test.db` file.
3. Navigate to `Examples/` and run `python seed_db.py` to reinitialize the test database.
4. Run `./run.py` to run the webserver, or you can find any of the example scripts in `Examples/`.
5. The API can be found at `http://localhost:5000/`. Use the routes in `klap4/api.py` to test it out if you desire.

### Project Structure
- There are two scripts in the project's root directory. `setup.py` sets up the `klap4` drectory as a package, while `run.py` runs the Flask web server.
- The `Dummy DB Data/` folder contains yaml files for seeding the test database.
- The `Examples/` folder contains a number of useful scripts to test functionality:
    - `db_query_example.py` can be used for testing queries using SQLAlchemy.
    - `ldap_connect.py` tests a connection to KMNR's LDAP server.
    - `logging_test.py` tests the database's software logging capabilities.
    - `seed_db.py` needs to be run to initialize the test database.
- Finally, the `klap4` package itself:
    - The `api/` folder contains helper functions and classes for use with Flask.
    - The `db_entities/` folder contains Python files for the different database objects.
        - `__init__.py` contains useful functions for interacting with the database.
    - `api.py` contains all the REST API endpoints.
    - `db.py` is used to configure logging for the database.
