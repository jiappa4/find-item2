# Flask API 서버 - 고급 검색 로직 적용

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import re
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app)  # CORS 허용

DB_PATH = 'prices.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def tokenize(text):
    """텍스트를 토큰으로 분리"""
    # 소문자 변환 및 특수문자 제거
    cleaned = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
    return set(cleaned.split())

def calculate_similarity(query_tokens, product_name, product_model, product_brand):
    """
    검색 유사도 점수 계산
    - 토큰 매칭: 검색어 토큰이 상품명에 얼마나 포함되는지
    - 모델명 정확도: 모델명 일치 여부
    - 브랜드 일치: 브랜드 일치 여부
    """
    product_tokens = tokenize(product_name)
    
    # 1. 토큰 매칭 점수 (0~70점)
    matched_tokens = query_tokens & product_tokens
    token_score = (len(matched_tokens) / len(query_tokens)) * 70 if query_tokens else 0
    
    # 2. 모델명 정확도 (0~20점)
    model_score = 0
    if product_model:
        # 검색어에 모델명이 포함되어 있는지
        query_lower = ' '.join(query_tokens).lower()
        model_lower = product_model.lower()
        
        if model_lower in query_lower or query_lower in model_lower:
            model_score = 20
        else:
            # 부분 매칭 (SequenceMatcher 사용)
            similarity = SequenceMatcher(None, query_lower, model_lower).ratio()
            model_score = similarity * 20
    
    # 3. 브랜드 일치 (0~10점)
    brand_score = 0
    if product_brand and product_brand.lower() in ' '.join(query_tokens).lower():
        brand_score = 10
    
    total_score = token_score + model_score + brand_score
    return total_score

def advanced_search(query):
    """
    고급 검색 로직
    1. 기본 LIKE 검색으로 후보 추출
    2. 각 후보에 유사도 점수 부여
    3. 점수 기준 필터링 및 정렬
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1단계: 넓은 범위 검색 (LIKE)
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
    
    # 2단계: 유사도 점수 계산
    scored_products = []
    for row in rows:
        score = calculate_similarity(
            query_tokens,
            row['name'],
            row['model_name'],
            row['brand']
        )
        
        # 최소 점수 필터링 (50점 이상만)
        if score >= 50:
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
    
    # 3단계: 점수순 정렬 후 가격순 정렬 (2차 정렬)
    scored_products.sort(key=lambda x: (-x['relevanceScore'], x['finalPrice']))
    
    return scored_products

@app.route('/api/search', methods=['GET'])
def search_products():
    """상품 검색 API - 고급 검색 로직 적용"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    # 고급 검색 실행
    products = advanced_search(query)
    
    # 통계 계산
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
