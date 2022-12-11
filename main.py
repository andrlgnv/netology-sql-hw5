import psycopg2

def create_db(conn):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(40) NOT NULL,
            last_name VARCHAR(40) NOT NULL,
            email TEXT UNIQUE
        );
        """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS phones(
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clients(id),
                phone VARCHAR(20) UNIQUE
                );
                """)

def add_client(conn, first_name, last_name, email):
    cur.execute("""
        INSERT INTO clients(first_name, last_name, email)
        VALUES(%s, %s, %s) RETURNING id;
        """, (first_name, last_name, email))

    print(f'Новый клиент добавлен: {cur.fetchone()[0]}')

def add_phone(conn, client_id, phone):
    cur.execute("""
               INSERT INTO phones(client_id, phone) VALUES(%s, %s);
               """, (client_id, phone))

    cur.execute("""
            SELECT first_name, last_name
            FROM clients AS cl
            JOIN phones AS p
            ON cl.id = p.client_id
            WHERE cl.id=%s;
            """, (client_id,))
    print(f'Номер телефона клиента {cur.fetchone()[1]} добавлен.')

def change_client(conn, id, first_name=None, last_name=None, email=None):
    cur.execute("""
        SELECT *
        FROM clients
        WHERE id=%s;
        """, (id,))
    client = cur.fetchone()
    if first_name is None:
        first_name = client[1]
    if last_name is None:
        last_name = client[2]
    if email is None:
        email = client[3]
    cur.execute("""
        UPDATE clients SET first_name=%s, last_name=%s, email=%s
        WHERE id=%s;
        """, (first_name, last_name, email, id))
    print(f'Данные клиента {last_name} обновлены.')

def delete_phone(conn, id, phone):
    cur.execute("""
        SELECT EXISTS(
        SELECT *
        FROM clients
        WHERE id=%s
        );
        """, (id,))
    client = cur.fetchone()[0]
    if client is False:
        print('Такого клиента нет.')
    else:
        cur.execute("""
            DELETE
            FROM phones
            WHERE phone=%s;
            """, (phone,))
        print(f'Телефон {phone} удален.')

def delete_client(conn, client_id):
    cur.execute("""
        DELETE FROM phones
        WHERE client_id=%s;
        """, (client_id,))
    cur.execute("""
        DELETE FROM clients
        WHERE id=%s;
        """, (client_id,))
    conn.commit()
    print('Все данные о клиенте удалены.')

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    if phone is not None:
        cur.execute("""
            SELECT cl.id FROM clients AS cl
            JOIN phones AS ph ON ph.client_id = cl.id
            WHERE ph.phone=%s;
            """, (phone,))
    else:
        cur.execute("""
            SELECT id FROM clients 
            WHERE first_name=%s or last_name=%s or email=%s;
            """, (first_name, last_name, email))
    print(cur.fetchall())


if __name__ == '__main__':
    with psycopg2.connect(database="clients_db", user="postgres", password="2007") as conn:
        with conn.cursor() as cur:
            create_db(conn)

            add_client(cur, 'Иван', 'Иванов', 'iivanov@gmail.com')
            add_client(cur, 'Мария', 'Сазонова', 'saz1212@gmail.com')
            add_client(cur, 'Кристиан', 'Белозубиков', 'cris666@gmail.com')
            add_client(cur, 'Вася', 'Васин', 'br@g.com')
            add_client(cur, 'Нина', 'Креветко', 'ni@g.com')
            add_client(cur, 'Максим', 'Иванов', 'iii@gmail.com')

            add_phone(conn, '2', '2344545')
            add_phone(conn, '1', '7774534')
            add_phone(conn, '3', '4552333')

            change_client(conn, '1', 'Семен')
            change_client(conn, '2', None, 'Логозина')
            change_client(conn, '3', None, None, 'belozub@gmail.com')
            change_client(conn, '2', None, None, None)

            delete_phone(conn, '1', '7774533')
            delete_phone(conn, '1', '7774534')

            find_client(conn, 'Мария')
            find_client(conn, None, 'Иванов')
            find_client(conn, None, None, 'belozub@gmail.com')
            find_client(conn, None, None, None, '2344545')

            delete_client(conn, 5)


