import mysql.connector
from contextlib import contextmanager

@contextmanager
def db_cur():
    my_db = None
    cursor = None
    try:
        my_db = mysql.connector.connect(
            host ="localhost",
            user = "root",
            password = "Yuval0611",
            database = "FlyTau",
            autocommit = True
        )
        cursor = my_db.cursor()
        yield cursor
    except mysql.connector.Error as err:
        raise err
    finally:
        if cursor:
            cursor.close()
        if my_db:
            my_db.close()


def get_all_active_airports():
    locations = []
    with db_cur() as cursor:
        query = """
        SELECT origin_airport FROM Route
        UNION
        SELECT dest_airport FROM Route
        ORDER BY origin_airport ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # התוצאה מגיעה כרשימה של טאפלים: [('TLV',), ('JFK',)]
        # נהפוך אותה לרשימה רגילה של מחרוזות: ['TLV', 'JFK']
        locations = [row[0] for row in results]

    return locations

class ExistingUser:
    def __init__(self,first_name,last_name,phone,email,passport_number,user_password,birth_date,registration_date):
        self.first_name=first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.passport_number = passport_number
        self.user_password = user_password
        self.birth_date = birth_date
        self.registration_date = registration_date

    @staticmethod
    def add(user):
        try:
            with db_cur() as cursor:
                query = "INSERT INTO ExistingUser (first_name,last_name,phone,email,passport_number,user_password,birth_date,registration_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(query, (user.first_name,user.last_name,user.phone,user.email,user.passport_number,user.user_password,user.birth_date,user.registration_date))
            return True
        except mysql.connector.Error:
            return False

    @staticmethod
    def get(user_email):
        with db_cur as cursor:
            cursor.execute("""SELECT c_password FROM Registered_Customer WHERE email=%s""",(user_email,))
            password=cursor.fetchone()
        return password
