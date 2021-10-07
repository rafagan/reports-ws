import psycopg2

from server.model import Visitor, VisitorVisit


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
                'INSERT INTO Visitor(id) VALUES(%s)',
                (visitor.id,)
            )


def insert_product(product):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Product(name, activityType) VALUES(%s, %s)',
                (
                    product.id,
                    product.name,
                    product.activity_type
                )
            )


def insert_sell(sell):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Sell(visitorId, productId) VALUES(%s, %d)',
                (
                    sell.visitor_id,
                    sell.product_id
                )
            )


def insert_visitor_visit(visit):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO VisitorVisit(date, durationSecs, isNew, visitorId) VALUES(%s, %s, %s, %s)',
                    (
                        visit.date,
                        visit.duration_secs,
                        visit.is_new,
                        visit.visitor_id
                    )
                )
            except Exception as e:
                print(visit, e)


def fetch_visitor(visitor_id):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Visitor WHERE id = %s', (visitor_id,))
            result = cursor.fetchone()
            return None if result is None else Visitor(*result)


def fetch_visitor_visit(visitor_visit_id):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM VisitorVisit WHERE id = %s', (visitor_visit_id,))
            result = cursor.fetchone()
            return None if result is None else VisitorVisit(*result)



def fetch_project(project_id):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Project WHERE id = %s', (project_id,))
            result = cursor.fetchone()
            return None if result is None else Visitor(*result)


