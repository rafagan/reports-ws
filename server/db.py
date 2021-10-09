from typing import Optional, List

import psycopg2

from server.model import Visitor, VisitorVisit, Product, ProductVisit, Sell


def gen_connection():
    connection = psycopg2.connect(
        user='report',
        password='XN5ZjSLPW8b6Nxs4',
        host="127.0.0.1",
        port="5432",
        database="report"
    )
    return connection


def insert_visitor(visitor: Visitor):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Visitor(id) VALUES(%s)',
                (visitor.id,)
            )


def insert_product(product: Product):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Product(id, name, activityType) VALUES(%s, %s, %s)',
                (
                    product.id,
                    product.name,
                    product.activity_type
                )
            )


def insert_product_visit(visit: ProductVisit):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO ProductVisit(date, productId) VALUES(%s, %s)',
                (
                    visit.date,
                    visit.product_id
                )
            )


def insert_sell(sell: Sell):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO Sell(visitorId, productId) VALUES(%s, %s)',
                (
                    sell.visitor_id,
                    sell.product_id
                )
            )


def insert_visitor_visit(visit: VisitorVisit):
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


def fetch_visitor(visitor_id: int):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Visitor WHERE id = %s', (visitor_id,))
            result = cursor.fetchone()
            return None if result is None else Visitor(*result)


def fetch_visitor_visit(visitor_visit_id: int):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM VisitorVisit WHERE id = %s', (visitor_visit_id,))
            result = cursor.fetchone()
            return None if result is None else VisitorVisit(*result)


def fetch_product(product_id: int) -> Optional[Product]:
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Product WHERE id = %s', (product_id,))
            result = cursor.fetchone()
            return None if result is None else Product(*result)


def query_daily_visits(month: int) -> List[VisitorVisit]:
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM VisitorVisit WHERE EXTRACT(MONTH FROM date) = %s',
                (month,)
            )
            results = cursor.fetchall()
            return [] if results is None else list(map(lambda r: VisitorVisit(*r), results))


def query_total_visits(month: int) -> int:
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) FROM VisitorVisit WHERE EXTRACT(MONTH FROM date) = %s',
                (month,)
            )
            result = cursor.fetchone()
            return result[0]


def query_total_new_visits(month: int) -> int:
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) FROM VisitorVisit WHERE EXTRACT(MONTH FROM date) = %s AND isNew = true',
                (month,)
            )
            result = cursor.fetchone()
            return result[0] or 0


def query_avg_engagement_time_secs(month: int) -> float:
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT AVG(durationSecs) FROM VisitorVisit WHERE EXTRACT(MONTH FROM date) = %s',
                (month,)
            )
            result = cursor.fetchone()
            return result[0] or 0


def query_total_receipt(month: int) -> float:
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT SUM(value) FROM Sell WHERE EXTRACT(MONTH FROM date) = %s',
                (month,)
            )
            result = cursor.fetchone()
            return result[0] / 100 or 0.0


def query_most_visited_products_by_activity_type(activity_type: str, amount):
    with gen_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) AS amount, p.activityType FROM Product as p '
                'INNER JOIN ProductVisit AS pv ON p.id = pv.productId '
                'GROUP BY p.activityType '
                'LIMIT %s;',
                (amount,)
            )
            results = cursor.fetchall()
            return [] if results is None else list(map(lambda r: {'amount': r[0], 'activity_type': r[1]}, results))


print(query_most_visited_products_by_activity_type('desconhecido', 7))
