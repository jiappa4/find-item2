# 가격 수집 배치 시스템 - 필터링 강화 버전

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import sqlite3
from datetime import datetime
import re

class PriceScraper:
    def __init__(self):
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 백그라운드 실행
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.db_path = 'prices.db'
        self.init_database()
        
        # 제외할 키워드 (악세서리, 부속품 등)
        self.exclude_keywords = [
            '케이스', '커버', '보호필름', '필름', '액정', '거치대', 
            '받침대', '스탠드', '가방', '파우치', '스티커', '데칼',
            '충전기', '어댑터', '케이블', '선', '리모컨', '부품',
            '악세사리', '액세서리', '교체용', '호환', '대체',
            '클리너', '청소', '세척', '필터', '먼지', '청소기',
            '수리', '부속', '연장', '확장'
        ]
        
        # 브랜드 리스트
        self.brands = [
            '신일', '삼성', 'LG', '애플', 'Apple', '샤오미', 'SK', 'KT',
            '다이슨', 'Dyson', '쿠쿠', 'CUCKOO', '필립스', 'Philips'
        ]
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query TEXT NOT NULL,
                shop TEXT NOT NULL,
                name TEXT NOT NULL,
                option_name TEXT,
                original_price INTEGER,
                discount_price INTEGER NOT NULL,
                shipping_fee INTEGER DEFAULT 0,
                final_price INTEGER NOT NULL,
                link TEXT,
                image_url TEXT,
                brand TEXT,
                model_name TEXT,
                search_tokens TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_search_query ON products(search_query)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_shop ON products(shop)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_brand ON products(brand)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_model_name ON products(model_name)
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def extract_price(self, price_text):
        """가격 텍스트에서 숫자만 추출"""
        if not price_text:
            return 0
        cleaned = re.sub(r'[^0-9]', '', price_text)
        return int(cleaned) if cleaned else 0
    
    def extract_brand_and_model(self, product_name, search_query):
        """
        상품명과 검색어에서 브랜드와 모델명 추출
        예: "신일 팬히터 SPH-1200" -> brand="신일", model="SPH-1200"
        """
        brand = None
        model = None
        
        # 브랜드 찾기
        for b in self.brands:
            if b in product_name or b in search_query:
                brand = b
                break
        
        # 모델명 추출: 영문+숫자 조합 (예: SPH-1200, iPhone15)
        model_patterns = [
            r'[A-Z]{2,}-?\d{3,}',  # SPH-1200, ABC-123
            r'[A-Z][a-z]+\s?\d+',  # iPhone15, Galaxy23
            r'\d{3,}[A-Z]*',       # 1200W, 2024A
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                model = match.group(0)
                break
        
        # 모델명이 없으면 검색어에서 브랜드 제외한 나머지
        if not model:
            tokens = search_query.split()
            model_tokens = [t for t in tokens if t != brand and len(t) > 1]
            model = ' '.join(model_tokens) if model_tokens else search_query
        
        return brand, model
    
    def generate_search_tokens(self, product_name, search_query):
        """검색 토큰 생성 (공백/특수문자 기준 분리)"""
        tokens = set()
        
        # 상품명 토큰화
        name_tokens = re.sub(r'[^\w\s가-힣]', ' ', product_name.lower()).split()
        tokens.update(name_tokens)
        
        # 검색어 토큰화
        query_tokens = re.sub(r'[^\w\s가-힣]', ' ', search_query.lower()).split()
        tokens.update(query_tokens)
        
        return '|'.join(tokens)
    
    def is_valid_product(self, name, query):
        """
        상품명이 실제 본품인지 검증
        - 검색어의 핵심 키워드 포함 여부 확인
        - 악세서리 키워드 제외
        """
        name_lower = name.lower()
        
        # 제외 키워드 체크
        for keyword in self.exclude_keywords:
            if keyword in name_lower:
                print(f"  ⚠️ 제외됨 (악세서리): {name}")
                return False
        
        # 검색어의 핵심 키워드 추출 (브랜드, 모델명 등)
        query_keywords = [k.strip() for k in query.split() if len(k.strip()) > 1]
        
        # 최소 2개 이상의 키워드가 포함되어야 함
        matched_count = 0
        for keyword in query_keywords:
            if keyword.lower() in name_lower:
                matched_count += 1
        
        if matched_count < max(2, len(query_keywords) * 0.6):  # 60% 이상 매칭
            print(f"  ⚠️ 제외됨 (매칭 부족): {name}")
            return False
        
        return True
    
    def scrape_naver_shopping(self, query):
        """네이버 쇼핑 가격 수집"""
        print(f"🔍 네이버쇼핑 검색 중: {query}")
        products = []
        
        try:
            url = f"https://search.shopping.naver.com/search/all?query={query}"
            self.driver.get(url)
            time.sleep(2)
            
            # 상품 리스트 대기
            items = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product_item__MDtDF"))
            )
            
            collected = 0
            for item in items:
                if collected >= 10:  # 상위 10개까지만 수집
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.product_title__Mmw2K a").text
                    
                    # 상품명 검증
                    if not self.is_valid_product(name, query):
                        continue
                    
                    # 가격 정보
                    price_elem = item.find_element(By.CSS_SELECTOR, "span.price_num__S2p_v em")
                    discount_price = self.extract_price(price_elem.text)
                    
                    # 너무 저렴하거나 비싼 경우 제외 (이상치)
                    if discount_price < 1000 or discount_price > 10000000:
                        print(f"  ⚠️ 제외됨 (가격 이상): {name} ({discount_price}원)")
                        continue
                    
                    # 배송비
                    try:
                        shipping_elem = item.find_element(By.CSS_SELECTOR, "span.product_delivery__RclQf")
                        shipping = 0 if "무료" in shipping_elem.text else 2500
                    except:
                        shipping = 2500
                    
                    # 링크
                    link = item.find_element(By.CSS_SELECTOR, "a.product_link__TrAac").get_attribute("href")
                    
                    # 이미지
                    try:
                        img = item.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    except:
                        img = ""
                    
                    products.append({
                        'shop': '네이버쇼핑',
                        'name': name,
                        'option': '단일',
                        'originalPrice': discount_price,
                        'discountPrice': discount_price,
                        'shipping': shipping,
                        'finalPrice': discount_price + shipping,
                        'link': link,
                        'image': img
                    })
                    collected += 1
                    print(f"  ✅ 수집: {name[:50]}... ({discount_price:,}원)")
                    
                except Exception as e:
                    continue
            
            print(f"  ✅ 총 {len(products)}개 상품 수집 완료")
            
        except Exception as e:
            print(f"  ❌ 네이버쇼핑 스크래핑 실패: {e}")
        
        return products
    
    def scrape_coupang(self, query):
        """쿠팡 가격 수집"""
        print(f"🔍 쿠팡 검색 중: {query}")
        products = []
        
        try:
            url = f"https://www.coupang.com/np/search?q={query}"
            self.driver.get(url)
            time.sleep(2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "li.search-product")
            
            collected = 0
            for item in items:
                if collected >= 10:
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.name").text
                    
                    if not self.is_valid_product(name, query):
                        continue
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "strong.price-value")
                    discount_price = self.extract_price(price_elem.text)
                    
                    if discount_price < 1000 or discount_price > 10000000:
                        continue
                    
                    # 로켓배송 확인
                    try:
                        item.find_element(By.CSS_SELECTOR, "span.badge.rocket")
                        shipping = 0
                    except:
                        shipping = 2500
                    
                    link_elem = item.find_element(By.CSS_SELECTOR, "a.search-product-link")
                    link = "https://www.coupang.com" + link_elem.get_attribute("href")
                    
                    try:
                        img = item.find_element(By.CSS_SELECTOR, "img.search-product-wrap-img").get_attribute("src")
                    except:
                        img = ""
                    
                    products.append({
                        'shop': '쿠팡',
                        'name': name,
                        'option': '단일',
                        'originalPrice': discount_price,
                        'discountPrice': discount_price,
                        'shipping': shipping,
                        'finalPrice': discount_price + shipping,
                        'link': link,
                        'image': img
                    })
                    collected += 1
                    print(f"  ✅ 수집: {name[:50]}... ({discount_price:,}원)")
                    
                except Exception as e:
                    continue
            
            print(f"  ✅ 총 {len(products)}개 상품 수집 완료")
            
        except Exception as e:
            print(f"  ❌ 쿠팡 스크래핑 실패: {e}")
        
        return products
    
    def scrape_gmarket(self, query):
        """G마켓 가격 수집"""
        print(f"🔍 G마켓 검색 중: {query}")
        products = []
        
        try:
            url = f"https://browse.gmarket.co.kr/search?keyword={query}"
            self.driver.get(url)
            time.sleep(2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.box__item-container")
            
            collected = 0
            for item in items:
                if collected >= 10:
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "span.text__item").text
                    
                    if not self.is_valid_product(name, query):
                        continue
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "strong.text__value")
                    discount_price = self.extract_price(price_elem.text)
                    
                    if discount_price < 1000 or discount_price > 10000000:
                        continue
                    
                    shipping = 2500
                    
                    link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    
                    try:
                        img = item.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    except:
                        img = ""
                    
                    products.append({
                        'shop': 'G마켓',
                        'name': name,
                        'option': '단일',
                        'originalPrice': discount_price,
                        'discountPrice': discount_price,
                        'shipping': shipping,
                        'finalPrice': discount_price + shipping,
                        'link': link,
                        'image': img
                    })
                    collected += 1
                    print(f"  ✅ 수집: {name[:50]}... ({discount_price:,}원)")
                    
                except Exception as e:
                    continue
            
            print(f"  ✅ 총 {len(products)}개 상품 수집 완료")
            
        except Exception as e:
            print(f"  ❌ G마켓 스크래핑 실패: {e}")
        
        return products
    
    def save_to_db(self, query, products):
        """수집한 데이터를 DB에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 데이터 삭제 (같은 검색어)
        cursor.execute("DELETE FROM products WHERE search_query = ?", (query,))
        
        # 새 데이터 저장
        for product in products:
            # 브랜드/모델명 추출
            brand, model = self.extract_brand_and_model(product['name'], query)
            search_tokens = self.generate_search_tokens(product['name'], query)
            
            cursor.execute('''
                INSERT INTO products 
                (search_query, shop, name, option_name, original_price, 
                 discount_price, shipping_fee, final_price, link, image_url,
                 brand, model_name, search_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query,
                product['shop'],
                product['name'],
                product['option'],
                product['originalPrice'],
                product['discountPrice'],
                product['shipping'],
                product['finalPrice'],
                product['link'],
                product.get('image', ''),
                brand,
                model,
                search_tokens
            ))
        
        conn.commit()
        conn.close()
        print(f"💾 DB에 {len(products)}개 상품 저장 완료")
    
    def export_to_json(self, query):
        """DB 데이터를 JSON으로 내보내기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT shop, name, option_name, original_price, discount_price, 
                   shipping_fee, final_price, link, image_url, updated_at
            FROM products 
            WHERE search_query = ?
            ORDER BY final_price ASC
        ''', (query,))
        
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for row in rows:
            products.append({
                'shop': row[0],
                'name': row[1],
                'option': row[2],
                'originalPrice': row[3],
                'discountPrice': row[4],
                'shipping': row[5],
                'finalPrice': row[6],
                'link': row[7],
                'image': row[8],
                'updatedAt': row[9]
            })
        
        # JSON 파일로 저장
        filename = f"data_{query.replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'count': len(products),
                'updatedAt': datetime.now().isoformat(),
                'products': products
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📄 {filename} 생성 완료")
        return filename
    
    def run_batch(self, queries):
        """배치 실행"""
        print("=" * 50)
        print("🚀 가격 수집 배치 시작 (필터링 강화)")
        print("=" * 50)
        print()
        
        for query in queries:
            print(f"\n{'='*50}")
            print(f"검색어: {query}")
            print('='*50)
            
            all_products = []
            
            # 각 쇼핑몰에서 수집
            all_products.extend(self.scrape_naver_shopping(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_coupang(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_gmarket(query))
            time.sleep(1)
            
            # 중복 제거 (같은 이름의 상품)
            unique_products = []
            seen_names = set()
            for product in all_products:
                name_key = product['name'].lower()[:50]  # 첫 50자로 비교
                if name_key not in seen_names:
                    unique_products.append(product)
                    seen_names.add(name_key)
            
            print(f"\n📊 중복 제거: {len(all_products)}개 → {len(unique_products)}개")
            
            # DB 저장
            if unique_products:
                self.save_to_db(query, unique_products)
                self.export_to_json(query)
            else:
                print("⚠️ 수집된 상품이 없습니다")
            
            print()
        
        print("=" * 50)
        print("✅ 배치 완료")
        print("=" * 50)
    
    def close(self):
        """리소스 정리"""
        self.driver.quit()


if __name__ == "__main__":
    # 수집할 검색어 목록
    search_queries = [
        "신일 팬히터 1200",
        "다이슨 청소기 V11",
        "삼성 갤럭시 버즈2"
    ]
    
    scraper = PriceScraper()
    
    try:
        scraper.run_batch(search_queries)
    finally:
        scraper.close()
