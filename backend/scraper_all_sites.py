# 전체 온라인 쇼핑몰 가격 수집 시스템

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

class PriceScraperAllSites:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.db_path = 'prices.db'
        self.init_database()
        
        # 제외 키워드
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
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_query ON products(search_query)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_shop ON products(shop)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_brand ON products(brand)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_name ON products(model_name)')
        
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
        """브랜드와 모델명 추출"""
        brand = None
        model = None
        
        for b in self.brands:
            if b in product_name or b in search_query:
                brand = b
                break
        
        model_patterns = [
            r'[A-Z]{2,}-?\d{3,}',
            r'[A-Z][a-z]+\s?\d+',
            r'\d{3,}[A-Z]*',
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                model = match.group(0)
                break
        
        if not model:
            tokens = search_query.split()
            model_tokens = [t for t in tokens if t != brand and len(t) > 1]
            model = ' '.join(model_tokens) if model_tokens else search_query
        
        return brand, model
    
    def generate_search_tokens(self, product_name, search_query):
        """검색 토큰 생성"""
        tokens = set()
        name_tokens = re.sub(r'[^\w\s가-힣]', ' ', product_name.lower()).split()
        tokens.update(name_tokens)
        query_tokens = re.sub(r'[^\w\s가-힣]', ' ', search_query.lower()).split()
        tokens.update(query_tokens)
        return '|'.join(tokens)
    
    def is_valid_product(self, name, query):
        """상품명 검증"""
        name_lower = name.lower()
        
        for keyword in self.exclude_keywords:
            if keyword in name_lower:
                print(f"  ⚠️ 제외됨 (악세서리): {name}")
                return False
        
        query_keywords = [k.strip() for k in query.split() if len(k.strip()) > 1]
        matched_count = sum(1 for keyword in query_keywords if keyword.lower() in name_lower)
        
        if matched_count < max(2, len(query_keywords) * 0.6):
            print(f"  ⚠️ 제외됨 (매칭 부족): {name}")
            return False
        
        return True
    
    def scrape_naver_shopping(self, query):
        """네이버쇼핑 수집"""
        print(f"🔍 네이버쇼핑 검색: {query}")
        products = []
        
        try:
            url = f"https://search.shopping.naver.com/search/all?query={query}"
            self.driver.get(url)
            time.sleep(2)
            
            items = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product_item__MDtDF"))
            )
            
            collected = 0
            for item in items:
                if collected >= 10:
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.product_title__Mmw2K a").text
                    if not self.is_valid_product(name, query):
                        continue
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "span.price_num__S2p_v em")
                    discount_price = self.extract_price(price_elem.text)
                    
                    if discount_price < 1000 or discount_price > 10000000:
                        continue
                    
                    try:
                        shipping_elem = item.find_element(By.CSS_SELECTOR, "span.product_delivery__RclQf")
                        shipping = 0 if "무료" in shipping_elem.text else 2500
                    except:
                        shipping = 2500
                    
                    link = item.find_element(By.CSS_SELECTOR, "a.product_link__TrAac").get_attribute("href")
                    
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
            
            print(f"  ✅ 네이버쇼핑 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ 네이버쇼핑 실패: {e}")
        
        return products
    
    def scrape_coupang(self, query):
        """쿠팡 수집"""
        print(f"🔍 쿠팡 검색: {query}")
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
                    
                    try:
                        shipping_elem = item.find_element(By.CSS_SELECTOR, "span.shipping")
                        shipping = 0 if "무료" in shipping_elem.text else 2500
                    except:
                        shipping = 0
                    
                    link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    
                    try:
                        img = item.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
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
            
            print(f"  ✅ 쿠팡 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ 쿠팡 실패: {e}")
        
        return products
    
    def scrape_gmarket(self, query):
        """G마켓 수집"""
        print(f"🔍 G마켓 검색: {query}")
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
            
            print(f"  ✅ G마켓 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ G마켓 실패: {e}")
        
        return products
    
    def scrape_11st(self, query):
        """11번가 수집"""
        print(f"🔍 11번가 검색: {query}")
        products = []
        
        try:
            url = f"https://search.11st.co.kr/Search.tmall?kwd={query}"
            self.driver.get(url)
            time.sleep(2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.c_prd_item")
            
            collected = 0
            for item in items:
                if collected >= 10:
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.c_prd_name a").text
                    if not self.is_valid_product(name, query):
                        continue
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "span.c_prd_price em")
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
                        'shop': '11번가',
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
            
            print(f"  ✅ 11번가 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ 11번가 실패: {e}")
        
        return products
    
    def scrape_auction(self, query):
        """옥션 수집"""
        print(f"🔍 옥션 검색: {query}")
        products = []
        
        try:
            url = f"https://browse.auction.co.kr/search?keyword={query}"
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
                        'shop': '옥션',
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
            
            print(f"  ✅ 옥션 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ 옥션 실패: {e}")
        
        return products
    
    def scrape_ssg(self, query):
        """SSG닷컴 수집"""
        print(f"🔍 SSG닷컴 검색: {query}")
        products = []
        
        try:
            url = f"https://www.ssg.com/search.ssg?target=all&query={query}"
            self.driver.get(url)
            time.sleep(2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.cunit_prod")
            
            collected = 0
            for item in items:
                if collected >= 10:
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.cunit_title a").text
                    if not self.is_valid_product(name, query):
                        continue
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "em.ssg_price")
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
                        'shop': 'SSG닷컴',
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
            
            print(f"  ✅ SSG닷컴 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ SSG닷컴 실패: {e}")
        
        return products
    
    def scrape_lotte(self, query):
        """롯데온 수집"""
        print(f"🔍 롯데온 검색: {query}")
        products = []
        
        try:
            url = f"https://www.lotteon.com/search/search/search.ecn?render=search&platform=pc&q={query}"
            self.driver.get(url)
            time.sleep(2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.srchProductUnitWrap")
            
            collected = 0
            for item in items:
                if collected >= 10:
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.srchProductName a").text
                    if not self.is_valid_product(name, query):
                        continue
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "em.srchProductPrice")
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
                        'shop': '롯데온',
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
            
            print(f"  ✅ 롯데온 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ 롯데온 실패: {e}")
        
        return products
    
    def scrape_interpark(self, query):
        """인터파크 수집"""
        print(f"🔍 인터파크 검색: {query}")
        products = []
        
        try:
            url = f"https://shopping.interpark.com/search?q={query}"
            self.driver.get(url)
            time.sleep(2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "li.productList__item")
            
            collected = 0
            for item in items:
                if collected >= 10:
                    break
                    
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.productList__name").text
                    if not self.is_valid_product(name, query):
                        continue
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "span.productList__price")
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
                        'shop': '인터파크',
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
            
            print(f"  ✅ 인터파크 {len(products)}개 수집")
        except Exception as e:
            print(f"  ❌ 인터파크 실패: {e}")
        
        return products
    
    def save_to_db(self, query, products):
        """DB 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM products WHERE search_query = ?", (query,))
        
        for product in products:
            brand, model = self.extract_brand_and_model(product['name'], query)
            search_tokens = self.generate_search_tokens(product['name'], query)
            
            cursor.execute('''
                INSERT INTO products 
                (search_query, shop, name, option_name, original_price, 
                 discount_price, shipping_fee, final_price, link, image_url,
                 brand, model_name, search_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query, product['shop'], product['name'], product['option'],
                product['originalPrice'], product['discountPrice'],
                product['shipping'], product['finalPrice'],
                product['link'], product.get('image', ''),
                brand, model, search_tokens
            ))
        
        conn.commit()
        conn.close()
        print(f"💾 DB에 {len(products)}개 저장")
    
    def export_to_json(self, query):
        """JSON 내보내기"""
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
                'shop': row[0], 'name': row[1], 'option': row[2],
                'originalPrice': row[3], 'discountPrice': row[4],
                'shipping': row[5], 'finalPrice': row[6],
                'link': row[7], 'image': row[8], 'updatedAt': row[9]
            })
        
        filename = f"data_{query.replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'count': len(products),
                'updatedAt': datetime.now().isoformat(),
                'products': products
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📄 {filename} 생성")
        return filename
    
    def run_batch(self, queries):
        """배치 실행 - 모든 쇼핑몰 수집"""
        print("="*60)
        print("🚀 전체 온라인 쇼핑몰 가격 수집 시작")
        print("📍 수집 대상: 네이버쇼핑, 쿠팡, G마켓, 11번가, 옥션, SSG, 롯데온, 인터파크")
        print("="*60)
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"🔍 검색어: {query}")
            print('='*60)
            
            all_products = []
            
            # 모든 쇼핑몰 수집
            all_products.extend(self.scrape_naver_shopping(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_coupang(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_gmarket(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_11st(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_auction(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_ssg(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_lotte(query))
            time.sleep(1)
            
            all_products.extend(self.scrape_interpark(query))
            time.sleep(1)
            
            # 중복 제거
            unique_products = []
            seen_names = set()
            for product in all_products:
                name_key = product['name'].lower()[:50]
                if name_key not in seen_names:
                    unique_products.append(product)
                    seen_names.add(name_key)
            
            print(f"\n📊 수집 결과: {len(all_products)}개 → 중복제거 후 {len(unique_products)}개")
            
            if unique_products:
                self.save_to_db(query, unique_products)
                self.export_to_json(query)
            else:
                print("⚠️ 수집된 상품 없음")
        
        print("\n" + "="*60)
        print("✅ 전체 쇼핑몰 수집 완료")
        print("="*60)
    
    def close(self):
        """리소스 정리"""
        self.driver.quit()


if __name__ == "__main__":
    search_queries = [
        "신일 팬히터 1200",
        "다이슨 청소기 V11",
        "삼성 갤럭시 버즈2"
    ]
    
    scraper = PriceScraperAllSites()
    
    try:
        scraper.run_batch(search_queries)
    finally:
        scraper.close()
