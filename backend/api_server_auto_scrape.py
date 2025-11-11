# Flask API 서버 - 자동 스크래핑 + 로딩바 기능

from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import re
from difflib import SequenceMatcher
import subprocess
import threading
import os
import sys

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

DB_PATH = 'prices.db'

scraping_status = {
    'is_scraping': False,
    'query': '',
    'progress': 0,
    'current_site': '',
    'total_sites': 8,
    'collected_count': 0,
    'message': ''
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def tokenize(text):
    cleaned = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
    return set(cleaned.split())

def calculate_similarity(query_tokens, product_name, product_model, product_brand):
    product_tokens = tokenize(product_name)
    matched_tokens = query_tokens & product_tokens
    token_score = (len(matched_tokens) / len(query_tokens)) * 70 if query_tokens else 0
    
    model_score = 0
    if product_model:
        query_lower = ' '.join(query_tokens).lower()
        model_lower = product_model.lower()
        if model_lower in query_lower or query_lower in model_lower:
            model_score = 20
        else:
            similarity = SequenceMatcher(None, query_lower, model_lower).ratio()
            model_score = similarity * 20
    
    brand_score = 10 if product_brand and product_brand.lower() in ' '.join(query_tokens).lower() else 0
    return token_score + model_score + brand_score

def advanced_search(query, min_score=70):
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
        score = calculate_similarity(query_tokens, row['name'], row['model_name'], row['brand'])
        if score >= min_score:
            scored_products.append({
                'shop': row['shop'], 'name': row['name'], 'option': row['option_name'],
                'originalPrice': row['original_price'], 'discountPrice': row['discount_price'],
                'shipping': row['shipping_fee'], 'finalPrice': row['final_price'],
                'link': row['link'], 'image': row['image_url'], 'updatedAt': row['updated_at'],
                'relevanceScore': round(score, 1)
            })
    
    scored_products.sort(key=lambda x: (-x['relevanceScore'], x['finalPrice']))
    return scored_products

def run_scraper(query):
    global scraping_status
    try:
        scraping_status.update({
            'is_scraping': True, 'query': query, 'progress': 0,
            'message': '스크래핑 시작...', 'collected_count': 0
        })
        
        script = f'''
import sys
sys.path.insert(0, 'backend')
from scraper_all_sites import PriceScraperAllSites
scraper = PriceScraperAllSites()
try:
    scraper.run_batch(["{query}"])
finally:
    scraper.close()
'''
        with open('temp_scraper.py', 'w', encoding='utf-8') as f:
            f.write(script)
        
        sites = ['네이버쇼핑', '쿠팡', 'G마켓', '11번가', '옥션', 'SSG', '롯데온', '인터파크']
        process = subprocess.Popen([sys.executable, 'temp_scraper.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, encoding='utf-8')
        
        for line in process.stdout:
            for i, site in enumerate(sites):
                if site in line and '검색' in line:
                    scraping_status.update({
                        'current_site': site,
                        'progress': int((i + 1) / len(sites) * 100),
                        'message': f'{site} 수집 중...'
                    })
                    break
        
        process.wait()
        scraping_status.update({'progress': 100, 'message': '완료!'})
        if os.path.exists('temp_scraper.py'):
            os.remove('temp_scraper.py')
    except Exception as e:
        scraping_status['message'] = f'오류: {str(e)}'
    finally:
        scraping_status['is_scraping'] = False

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/scraping/status', methods=['GET'])
def get_scraping_status():
    return jsonify(scraping_status)

@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    if scraping_status['is_scraping']:
        return jsonify({'error': '이미 스크래핑 중'}), 400
    
    query = request.get_json().get('query', '').strip()
    if not query:
        return jsonify({'error': '검색어 필요'}), 400
    
    thread = threading.Thread(target=run_scraper, args=(query,))
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': '검색어 필요'}), 400
    
    products = advanced_search(query, min_score=70)
    
    if not products:
        return jsonify({'needsScraping': True, 'query': query})
    
    lowest = min(p['finalPrice'] for p in products)
    avg_price = sum(p['finalPrice'] for p in products) / len(products)
    free_shipping = sum(1 for p in products if p['shipping'] == 0)
    avg_relevance = sum(p['relevanceScore'] for p in products) / len(products)
    
    return jsonify({
        'query': query, 'products': products,
        'summary': {
            'lowestPrice': lowest, 'avgPrice': int(avg_price),
            'totalCount': len(products),
            'freeShippingRate': round(free_shipping / len(products) * 100, 1),
            'avgRelevance': round(avg_relevance, 1)
        },
        'updatedAt': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 API 서버 시작 (자동 스크래핑)")
    app.run(debug=True, host='0.0.0.0', port=5000)
