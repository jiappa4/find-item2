# Flask API 서버

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # CORS 허용

DB_PATH = 'prices.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/search', methods=['GET'])
def search_products():
    """상품 검색 API"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # LIKE 검색으로 부분 일치
    cursor.execute('''
        SELECT shop, name, option_name, original_price, discount_price,
               shipping_fee, final_price, link, image_url, updated_at
        FROM products
        WHERE search_query LIKE ?
        ORDER BY final_price ASC
    ''', (f'%{query}%',))
    
    rows = cursor.fetchall()
    conn.close()
    
    products = []
    for row in rows:
        products.append({
            'shop': row['shop'],
            'name': row['name'],
            'option': row['option_name'],
            'originalPrice': row['original_price'],
            'discountPrice': row['discount_price'],
            'shipping': row['shipping_fee'],
            'finalPrice': row['final_price'],
            'link': row['link'],
            'image': row['image_url'],
            'updatedAt': row['updated_at']
        })
    
    # 통계 계산
    if products:
        avg_price = sum(p['finalPrice'] for p in products) / len(products)
        free_shipping_count = sum(1 for p in products if p['shipping'] == 0)
        
        summary = {
            'totalCount': len(products),
            'lowestPrice': products[0]['finalPrice'],
            'avgPrice': int(avg_price),
            'freeShippingRate': int((free_shipping_count / len(products)) * 100)
        }
    else:
        summary = None
    
    return jsonify({
        'query': query,
        'count': len(products),
        'summary': summary,
        'products': products,
        'updatedAt': datetime.now().isoformat()
    })

@app.route('/api/products', methods=['GET'])
def get_all_products():
    """전체 상품 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT search_query, COUNT(*) as count, MAX(updated_at) as last_updated
        FROM products
        GROUP BY search_query
        ORDER BY last_updated DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    queries = []
    for row in rows:
        queries.append({
            'query': row['search_query'],
            'count': row['count'],
            'lastUpdated': row['last_updated']
        })
    
    return jsonify({
        'queries': queries,
        'totalQueries': len(queries)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """통계 정보"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 전체 상품 수
    cursor.execute('SELECT COUNT(*) as total FROM products')
    total = cursor.fetchone()['total']
    
    # 검색어 수
    cursor.execute('SELECT COUNT(DISTINCT search_query) as queries FROM products')
    queries = cursor.fetchone()['queries']
    
    # 쇼핑몰별 상품 수
    cursor.execute('''
        SELECT shop, COUNT(*) as count
        FROM products
        GROUP BY shop
        ORDER BY count DESC
    ''')
    shops = [{'shop': row['shop'], 'count': row['count']} for row in cursor.fetchall()]
    
    # 최근 업데이트
    cursor.execute('SELECT MAX(updated_at) as last_update FROM products')
    last_update = cursor.fetchone()['last_update']
    
    conn.close()
    
    return jsonify({
        'totalProducts': total,
        'totalQueries': queries,
        'shopStats': shops,
        'lastUpdate': last_update
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Flask API Server Starting...")
    print("📍 http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
