# Flask API 서버 - CORS 완전 해결 버전

from flask import Flask, jsonify, request
import sqlite3
import json
from datetime import datetime
import re
from difflib import SequenceMatcher

app = Flask(__name__)

# CORS를 수동으로 처리 (flask-cors 없이)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

DB_PATH = 'prices.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def tokenize(text):
    """텍스트를 토큰으로 분리"""
    cleaned = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
    return set(cleaned.split())

def calculate_similarity(query_tokens, product_name, product_model, product_brand):
    """검색 유사도 점수 계산"""
    product_tokens = tokenize(product_name)
    
    # 1. 토큰 매칭 점수 (0~70점)
    matched_tokens = query_tokens & product_tokens
    token_score = (len(matched_tokens) / len(query_tokens)) * 70 if query_tokens else 0
    
    # 2. 모델명 정확도 (0~20점)
    model_score = 0
    if product_model:
        query_lower = ' '.join(query_tokens).lower()
        model_lower = product_model.lower()
        
        if model_lower in query_lower or query_lower in model_lower:
            model_score = 20
        else:
            similarity = SequenceMatcher(None, query_lower, model_lower).ratio()
            model_score = similarity * 20
    
    # 3. 브랜드 일치 (0~10점)
    brand_score = 0
    if product_brand and product_brand.lower() in ' '.join(query_tokens).lower():
        brand_score = 10
    
    total_score = token_score + model_score + brand_score
    return total_score

def advanced_search(query):
    """고급 검색 로직 - 70점 이상만 필터링"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_tokens = tokenize(query)
    like_pattern = '%' + '%'.join(query_tokens) + '%'
    
    cursor.execute('''
        SELECT id, shop, name, option_name, original_price, discount_price,
               shipping_fee, final_price, link, image_url, updated_at,
               brand, model_name, search_tokens
        FROM products
        WHERE search_query LIKE ? OR name LIKE ? OR search_tokens LIKE ?
    ''', (f'%{query}%', like_pattern, like_pattern))
    
    rows = cursor.fetchall()
    conn.close()
    
    scored_products = []
    for row in rows:
        score = calculate_similarity(
            query_tokens,
            row['name'],
            row['model_name'],
            row['brand']
        )
        
        # 70점 이상만 포함 (50 -> 70으로 변경)
        if score >= 70:
            scored_products.append({
                'shop': row['shop'],
                'name': row['name'],
                'option': row['option_name'],
                'originalPrice': row['original_price'],
                'discountPrice': row['discount_price'],
                'shipping': row['shipping_fee'],
                'finalPrice': row['final_price'],
                'link': row['link'],
                'image': row['image_url'],
                'updatedAt': row['updated_at'],
                'brand': row['brand'],
                'model': row['model_name'],
                'relevanceScore': round(score, 1)
            })
    
    scored_products.sort(key=lambda x: (-x['relevanceScore'], x['finalPrice']))
    return scored_products

@app.route('/api/search', methods=['GET', 'OPTIONS'])
def search_products():
    """상품 검색 API"""
    if request.method == 'OPTIONS':
        return '', 204
        
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    products = advanced_search(query)
    
    if products:
        avg_price = sum(p['finalPrice'] for p in products) / len(products)
        free_shipping_count = sum(1 for p in products if p['shipping'] == 0)
        avg_relevance = sum(p['relevanceScore'] for p in products) / len(products)
        
        summary = {
            'totalCount': len(products),
            'lowestPrice': products[0]['finalPrice'] if products else 0,
            'avgPrice': int(avg_price),
            'freeShippingRate': int((free_shipping_count / len(products)) * 100),
            'avgRelevance': round(avg_relevance, 1)
        }
    else:
        summary = None
    
    return jsonify({
        'query': query,
        'count': len(products),
        'summary': summary,
        'products': products,
        'updatedAt': datetime.now().isoformat(),
        'searchMethod': 'advanced'
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
    
    cursor.execute('SELECT COUNT(*) as total FROM products')
    total = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(DISTINCT search_query) as queries FROM products')
    queries = cursor.fetchone()['queries']
    
    cursor.execute('''
        SELECT shop, COUNT(*) as count
        FROM products
        GROUP BY shop
        ORDER BY count DESC
    ''')
    shops = [{'shop': row['shop'], 'count': row['count']} for row in cursor.fetchall()]
    
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

@app.route('/')
def index():
    """루트 경로"""
    return jsonify({
        'message': 'Price Comparison API',
        'version': '3.1',
        'relevanceThreshold': 70,
        'endpoints': {
            'search': '/api/search?q=query',
            'products': '/api/products',
            'stats': '/api/stats',
            'health': '/api/health'
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("Flask API Server Starting...")
    print("=" * 50)
    print("Server: http://localhost:5000")
    print("Server: http://127.0.0.1:5000")
    print("=" * 50)
    print("CORS: Enabled for all origins")
    print("Relevance Threshold: 70+ points")
    print("=" * 50)
    print("Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/search?q=query")
    print("  GET  /api/products")
    print("  GET  /api/stats")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
