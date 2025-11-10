# DB 스키마 마이그레이션 스크립트
# model_name, brand 필드 추가 및 기존 데이터 파싱

import sqlite3
import re
from datetime import datetime

DB_PATH = 'prices.db'

def extract_model_and_brand(product_name, search_query):
    """
    상품명에서 브랜드와 모델명 추출
    예: "신일 팬히터 SPH-1200 블랙" -> brand="신일", model="SPH-1200"
    """
    # 브랜드 리스트 (확장 가능)
    brands = ['신일', '삼성', 'LG', '애플', 'Apple', '샤오미', 'SK', 'KT']
    
    brand = None
    model = None
    
    # 브랜드 찾기
    for b in brands:
        if b in product_name or b in search_query:
            brand = b
            break
    
    # 검색어에서 브랜드 제외한 나머지를 모델명으로
    if brand:
        # 검색어를 토큰화
        tokens = search_query.split()
        model_tokens = [t for t in tokens if t != brand]
        model = ' '.join(model_tokens)
    else:
        model = search_query
    
    # 모델명에서 영문+숫자 조합 추출 (예: SPH-1200)
    model_code_match = re.search(r'[A-Z]{2,}-?\d{3,}', product_name, re.IGNORECASE)
    if model_code_match:
        model = model_code_match.group(0)
    
    return brand, model

def migrate_database():
    """DB 스키마 마이그레이션 실행"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 DB 마이그레이션 시작...")
    
    try:
        # 1. 새 컬럼 추가
        cursor.execute('ALTER TABLE products ADD COLUMN brand TEXT')
        print("✅ brand 컬럼 추가 완료")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("ℹ️  brand 컬럼 이미 존재")
        else:
            raise
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN model_name TEXT')
        print("✅ model_name 컬럼 추가 완료")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("ℹ️  model_name 컬럼 이미 존재")
        else:
            raise
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN search_tokens TEXT')
        print("✅ search_tokens 컬럼 추가 완료")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("ℹ️  search_tokens 컬럼 이미 존재")
        else:
            raise
    
    # 2. 기존 데이터 업데이트
    cursor.execute('SELECT id, name, search_query FROM products WHERE brand IS NULL')
    rows = cursor.fetchall()
    
    updated_count = 0
    for row in rows:
        product_id, name, search_query = row
        brand, model = extract_model_and_brand(name, search_query)
        
        # 검색 토큰 생성 (공백 기준 분리)
        tokens = set(name.lower().split() + search_query.lower().split())
        search_tokens = '|'.join(tokens)
        
        cursor.execute('''
            UPDATE products 
            SET brand = ?, model_name = ?, search_tokens = ?
            WHERE id = ?
        ''', (brand, model, search_tokens, product_id))
        
        updated_count += 1
    
    # 3. 인덱스 생성
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_brand ON products(brand)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_name ON products(model_name)')
        print("✅ 인덱스 생성 완료")
    except:
        print("ℹ️  인덱스 이미 존재")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {updated_count}개 레코드 업데이트 완료")
    print("🎉 마이그레이션 완료!")

if __name__ == '__main__':
    migrate_database()
