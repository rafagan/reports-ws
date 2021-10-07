import psycopg2


def gen_connection():
    connection = psycopg2.connect(
        user='report',
        password='XN5ZjSLPW8b6Nxs4',
        host="127.0.0.1",
        port="5432",
        database="report"
    )
    return connection


def insert_visitor(visitor):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Visitor (id) VALUES (%s)',
                (visitor.id,)
            )


def insert_product(product):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Product (name, activityType) VALUES (%s, %s)',
                product.id,
                product.name,
                product.activity_type
            )


def insert_sell(sell):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Sell (visitorId, productId) VALUES (%s, %d)',
                sell.visitor_id,
                sell.product_id
            )


def insert_visitor_visit(visit):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO VisitorVisit (date, durationSecs, isNew, visitorId) VALUES (%s, %d, %d, %s)',
                visit.date,
                visit.duration_secs,
                visit.is_new,
                visit.visitor_id
            )


def fetch_visitors():
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Visitor')
            return list(map(lambda item: {'id': item[0]}, cursor.fetchall()))


print(fetch_visitors())
