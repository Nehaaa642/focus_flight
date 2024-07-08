import mysql.connector

def call_api(email):
    host = 'localhost'
    user = 'root'
    password = ''
    database_name = 'avalanche'
    table_name = 'new_user'
    user_email = email

    def connect_to_database(host, user, password, database):
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = connection.cursor()
        return connection, cursor

    def generate_api(cursor, user_email):
        user_api = hash(user_email)
        command = "UPDATE new_user SET api_key = '" + str(user_api) + "' WHERE email = '" + email + "';"
        cursor.execute(command)
        connection.commit()

    def fetch_data(cursor, table_name):
        # print(table_name)
        command = "SELECT * FROM " + table_name + ";"
        modified_query = command.replace("'", "")
        cursor.execute(modified_query)
        return cursor.fetchall()

    def check_api(cursor, email, table):
        command = "SELECT CASE WHEN api_key IS NULL OR api_key = '' THEN 'Empty' ELSE 'Not Empty' END AS api_key FROM new_user WHERE email = '" + email + "';"
        cursor.execute(command)
        return cursor.fetchall()

    def get_api(cursor, email):
        command = "SELECT api_key FROM new_user WHERE email='" + email + "';"
        cursor.execute(command)
        ref = cursor.fetchall()
        return print(ref[0][0])

    connection, cursor = connect_to_database(host, user, password, database_name)
    sql_user_list = fetch_data(cursor, table_name)
    check = check_api(cursor, user_email, sql_user_list)

    if len(check) > 0:
        if 'Empty' in check[0]:
            # print("Oh no!")
            generate_api(cursor, user_email)
        else:
            # print("Already has a referral")
            return get_api(cursor, user_email)
    elif len(check) == 0:
        return print("Not registerd!")
    else:
        print("Ok")



if __name__ == "__main__":
    # Code to execute when the script is run directly
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else ""

    call_api(email)
