# Test search accuracy

import sqlite3
import re
from difflib import SequenceMatcher

DB_PATH = 'prices.db'

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
    return total_score, token_score, model_score, brand_score

def test_search(query):
    """검색 테스트"""
    print("=" * 80)
    print(f"Search Query: {query}")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query_tokens = tokenize(query)
    print(f"Query Tokens: {query_tokens}")
    print()
    
    like_pattern = '%' + '%'.join(query_tokens) + '%'
    
    cursor.execute('''
        SELECT id, shop, name, brand, model_name, final_price
        FROM products
        WHERE search_query LIKE ? OR name LIKE ? OR search_tokens LIKE ?
        LIMIT 30
    ''', (f'%{query}%', like_pattern, like_pattern))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(rows)} products before filtering")
    print()
    
    scored_products = []
    for row in rows:
        total_score, token_score, model_score, brand_score = calculate_similarity(
            query_tokens,
            row['name'],
            row['model_name'],
            row['brand']
        )
        
        scored_products.append({
            'name': row['name'],
            'brand': row['brand'],
            'model': row['model_name'],
            'price': row['final_price'],
            'total_score': round(total_score, 1),
            'token_score': round(token_score, 1),
            'model_score': round(model_score, 1),
            'brand_score': round(brand_score, 1)
        })
    
    # 점수순 정렬
    scored_products.sort(key=lambda x: -x['total_score'])
    
    # 상위 20개 출력
    print(f"{'Rank':<5} {'Score':<7} {'T/M/B':<12} {'Brand':<10} {'Model':<15} {'Name':<50}")
    print("-" * 100)
    
    for i, p in enumerate(scored_products[:20]):
        status = "✅" if p['total_score'] >= 50 else "❌"
        scores = f"{p['token_score']:.0f}/{p['model_score']:.0f}/{p['brand_score']:.0f}"
        print(f"{status} {i+1:<3} {p['total_score']:<7.1f} {scores:<12} {p['brand'] or 'N/A':<10} {p['model'] or 'N/A':<15} {p['name'][:45]:<50}")
    
    print()
    print(f"Products with score >= 50: {sum(1 for p in scored_products if p['total_score'] >= 50)}")
    print(f"Products with score < 50: {sum(1 for p in scored_products if p['total_score'] < 50)}")
    print()

if __name__ == '__main__':
    # Test cases
    test_search("신일 팬히터 1200")
    print("\n" * 2)
    test_search("다이슨 청소기 V11")
