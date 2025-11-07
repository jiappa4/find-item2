# 가격 수집 배치 시스템

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
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def extract_price(self, price_text):
        """가격 텍스트에서 숫자만 추출"""
        if not price_text:
            return 0
        cleaned = re.sub(r'[^0-9]', '', price_text)
        return int(cleaned) if cleaned else 0
    
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
            
            for item in items[:5]:  # 상위 5개만
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.product_title__Mmw2K a").text
                    
                    # 가격 정보
                    price_elem = item.find_element(By.CSS_SELECTOR, "span.price_num__S2p_v em")
                    discount_price = self.extract_price(price_elem.text)
                    
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
                    
                except Exception as e:
                    print(f"  ⚠️ 상품 파싱 실패: {e}")
                    continue
            
            print(f"  ✅ {len(products)}개 상품 수집 완료")
            
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
            
            for item in items[:5]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "div.name").text
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "strong.price-value")
                    discount_price = self.extract_price(price_elem.text)
                    
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
                    
                except Exception as e:
                    continue
            
            print(f"  ✅ {len(products)}개 상품 수집 완료")
            
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
            
            for item in items[:5]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "span.text__item").text
                    
                    price_elem = item.find_element(By.CSS_SELECTOR, "strong.text__value")
                    discount_price = self.extract_price(price_elem.text)
                    
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
                    
                except Exception as e:
                    continue
            
            print(f"  ✅ {len(products)}개 상품 수집 완료")
            
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
            cursor.execute('''
                INSERT INTO products 
                (search_query, shop, name, option_name, original_price, 
                 discount_price, shipping_fee, final_price, link, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                product.get('image', '')
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
        print("🚀 가격 수집 배치 시작")
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
            
            # DB 저장
            if all_products:
                self.save_to_db(query, all_products)
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
        "다이슨 청소기",
        "삼성 갤럭시 버즈"
    ]
    
    scraper = PriceScraper()
    
    try:
        scraper.run_batch(search_queries)
    finally:
        scraper.close()
