from flask import Flask, request

from server.db import gen_connection, query_daily_visits, query_total_visits, query_total_new_visits, \
    query_avg_engagement_time_secs, query_total_receipt, query_most_visited_products_by_activity_type

app = Flask(__name__)


@app.route('/visits/{month}', methods=['GET'])
def get_daily_visits(month):
    return {'status': 'ok', 'payload': query_daily_visits(month)}


@app.route('/visits/{month}/total', methods=['GET'])
def get_total_visits(month):
    return {'status': 'ok', 'payload': query_total_visits(month)}


@app.route('/visits/{month}/total/new', methods=['GET'])
def get_total_new_visits(month):
    return {'status': 'ok', 'payload': query_total_new_visits(month)}


@app.route('/visits/{month}/average/engagement', methods=['GET'])
def get_avg_engagement_time_secs(month):
    return {'status': 'ok', 'payload': query_avg_engagement_time_secs(month)}


@app.route('/sells/{month}/total', methods=['GET'])
def get_total_receipt(month):
    return {'status': 'ok', 'payload': query_total_receipt(month)}


@app.route('/products/{activity_type}', methods=['GET'])
def get_most_visited_product(activity_type):
    amount = request.args.get('amount', 7)
    return {
        'status': 'ok',
        'payload': query_most_visited_products_by_activity_type(activity_type, amount)
    }


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

