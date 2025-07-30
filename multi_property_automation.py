# multi_property_automation.py - 네이버부동산 매물 자동화 스크립트 (Template)

import asyncio
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright

class MultiPropertyAutomation:
    def __init__(self):
        # 환경변수에서 로그인 정보 가져오기 (필수)
        self.login_id = os.getenv('LOGIN_ID')
        self.login_pw = os.getenv('LOGIN_PASSWORD')
        
        # 환경변수 검증
        if not self.login_id or not self.login_pw:
            raise ValueError("❌ GitHub Secrets에 LOGIN_ID와 LOGIN_PASSWORD를 설정해주세요.")
        
        # 사이트 URL
        self.login_url = "https://www.aipartner.com/integrated/login?serviceCode=1000"
        self.ad_list_url = "https://www.aipartner.com/offerings/ad_list"
        
        # 환경변수에서 매물번호들 가져오기
        property_numbers_str = os.getenv('PROPERTY_NUMBERS', '')
        self.property_numbers = [
            num.strip() for num in property_numbers_str.split(',') 
            if num.strip()
        ]
        
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
        
        print(f"🔧 로그인 ID: {self.login_id}")
        print(f"🏠 처리할 매물: {len(self.property_numbers)}개")
        print(f"📋 매물번호: {', '.join(self.property_numbers)}")
        print(f"🧪 테스트 모드: {self.test_mode}")
    
    async def login(self, page):
        """로그인 처리"""
        print("🔗 로그인 페이지로 이동 중...")
        
        await page.goto(self.login_url, timeout=60000)
        await page.wait_for_selector('#member-id', timeout=30000)
        
        await page.fill('#member-id', self.login_id)
        await page.fill('#member-pw', self.login_pw)
        await page.click('#integrated-login > a')
        
        await page.wait_for_timeout(10000)
        
        # 로그인 성공 확인
        current_url = page.url
        title = await page.title()
        
        print(f"🔗 로그인 후 URL: {current_url}")
        print(f"📄 로그인 후 제목: {title}")
        
        is_login_page = any([
            'login' in current_url.lower(),
            '로그인' in title,
            await page.query_selector('#member-id')
        ])
        
        if is_login_page:
            print("❌ 로그인 실패")
            return False
        
        print("✅ 로그인 완료")
        return True
    
    async def process_single_property(self, page, property_number, index, total, retry=False):
        """단일 매물 처리 (페이지네이션 포함)"""
        retry_text = " (재시도)" if retry else ""
        print(f"\n{'='*60}")
        print(f"[{index}/{total}] 매물번호 {property_number} 처리 시작{retry_text}")
        print(f"{'='*60}")
        
        # 재시도인 경우 추가 대기
        if retry:
            print("🔄 재시도 모드: 안정성을 위해 추가 대기...")
            await page.wait_for_timeout(3000)
        
        try:
            # 매물 리스트 페이지로 이동
            await page.goto(self.ad_list_url, timeout=60000)
            await page.wait_for_timeout(3000)
            
            # 매물 검색 (페이지네이션 포함)
            property_found = False
            current_page = 1
            max_pages = 10
            
            while not property_found and current_page <= max_pages:
                print(f"📄 {current_page}페이지에서 매물 검색 중...")
                
                # 테이블 찾기
                await page.wait_for_selector('table tbody tr', timeout=30000)
                rows = await page.query_selector_all('table tbody tr')
                
                print(f"📊 {current_page}페이지 매물 수: {len(rows)}개")
                
                # 현재 페이지에서 매물 검색
                for i, row in enumerate(rows, 1):
                    try:
                        # 매물번호가 있는 셀 찾기 (더 정확한 방법)
                        number_cell = await row.query_selector('td:nth-child(3) > div.numberN')
                        if number_cell:
                            number_text = await number_cell.inner_text()
                            if property_number in number_text.strip():
                                print(f"🎯 매물번호 {property_number} 발견! ({current_page}페이지, 행 {i})")
                                
                                # 매물 정보 출력
                                await self.print_property_info(row, property_number)
                                
                                # 업데이트 실행
                                if self.test_mode:
                                    await self.simulate_update(property_number)
                                else:
                                    await self.execute_real_update(page, row, property_number)
                                
                                property_found = True
                                break
                    except Exception as e:
                        print(f"⚠️ 행 {i} 처리 중 오류: {e}")
                        continue
                
                if property_found:
                    break
                
                # 다음 페이지로 이동
                try:
                    next_button = await page.query_selector('#wrap > div > div > div > div.sectionWrap > div.singleSection.listSection > div.pagination > span:nth-child(5) > a')
                    if next_button:
                        button_class = await next_button.get_attribute('class')
                        if button_class and 'disabled' in button_class:
                            print(f"📄 마지막 페이지({current_page}페이지)에 도달했습니다.")
                            break
                        
                        await next_button.click()
                        await page.wait_for_timeout(3000)
                        current_page += 1
                        print(f"➡️ {current_page}페이지로 이동...")
                    else:
                        print("❌ 다음 페이지 버튼을 찾을 수 없습니다.")
                        break
                except Exception as e:
                    print(f"❌ 페이지 이동 중 오류: {e}")
                    break
            
            if not property_found:
                print(f"❌ 매물번호 {property_number}를 {current_page-1}페이지까지 검색했지만 찾을 수 없습니다.")
                return False
            
            print(f"✅ 매물번호 {property_number} 처리 완료")
            return True
            
        except Exception as e:
            print(f"❌ 매물번호 {property_number} 처리 실패: {e}")
            return False
    
    async def print_property_info(self, row, property_number):
        """매물 정보 출력"""
        try:
            cells = await row.query_selector_all('td')
            if len(cells) >= 6:
                name = await cells[1].inner_text() if len(cells) > 1 else "알 수 없음"
                trade_type = await cells[3].inner_text() if len(cells) > 3 else "알 수 없음"
                price = await cells[4].inner_text() if len(cells) > 4 else "알 수 없음"
                
                print(f"📋 매물 정보:")
                print(f"   번호: {property_number}")
                print(f"   매물명: {name.strip()}")
                print(f"   거래종류: {trade_type.strip()}")
                print(f"   가격: {price.strip()}")
        except Exception as e:
            print(f"⚠️ 매물 정보 추출 중 오류: {e}")
    
    async def simulate_update(self, property_number):
        """업데이트 시뮬레이션 (테스트 모드)"""
        print(f"\n🧪 매물번호 {property_number} 업데이트 시뮬레이션:")
        print("1️⃣ 노출종료 (시뮬레이션)")
        await asyncio.sleep(1)
        print("2️⃣ 광고종료 (시뮬레이션)")
        await asyncio.sleep(1)
        print("3️⃣ 재광고 (시뮬레이션)")
        await asyncio.sleep(1)
        print("4️⃣ 광고등록 (시뮬레이션)")
        await asyncio.sleep(1)
        print("5️⃣ 결제완료 (시뮬레이션)")
        print(f"🎉 매물번호 {property_number} 시뮬레이션 완료!")
    
    async def execute_real_update(self, page, row, property_number):
        """실제 업데이트 실행"""
        print(f"\n🚀 매물번호 {property_number} 실제 업데이트:")
        
        try:
            # 1. 노출종료
            print("1️⃣ 노출종료 버튼 클릭...")
            end_button = await row.query_selector('#naverEnd')
            if not end_button:
                print("❌ 노출종료 버튼을 찾을 수 없습니다.")
                return False
            
            await end_button.click()
            await page.wait_for_timeout(2000)
            print("   ✅ 노출종료 완료")
            
            # 2. 광고종료
            print("2️⃣ 광고종료 버튼 클릭...")
            ad_end_button = await page.wait_for_selector('.statusAdEnd', timeout=10000)
            await ad_end_button.click()
            await page.wait_for_timeout(3000)
            print("   ✅ 종료매물 목록 표시")
            
            # 3. 재광고
            print("3️⃣ 종료매물에서 재광고 버튼 검색...")
            end_rows = await page.query_selector_all('table tbody tr')
            
            for row in end_rows:
                number_cell = await row.query_selector('td:nth-child(3) > div.numberN')
                if number_cell:
                    number_text = await number_cell.inner_text()
                    if property_number in number_text.strip():
                        re_ad_button = await row.query_selector('#reReg')
                        if re_ad_button:
                            await re_ad_button.click()
                            await page.wait_for_timeout(3000)
                            print("   ✅ 재광고 버튼 클릭 완료")
                            break
            
            # 4. 광고등록
            print("4️⃣ 광고등록 페이지 처리...")
            await page.wait_for_url('**/offerings/ad_regist', timeout=30000)
            await page.wait_for_timeout(2000)
            
            await page.click('text=광고하기')
            await page.wait_for_timeout(2000)
            print("   ✅ 광고하기 버튼 클릭 완료")
            
            # 5. 결제
            print("5️⃣ 결제 처리...")
            await page.wait_for_timeout(3000)
            
            # JavaScript 방식으로 체크박스 클릭 (안정성)
            await page.evaluate("document.querySelector('#consentMobile2').click()")
            await page.wait_for_timeout(1000)
            print("   ✅ 체크박스 클릭 완료")
            
            payment_button = await page.query_selector('#naverSendSave')
            if payment_button:
                await payment_button.click()
                print("   ✅ 결제하기 버튼 클릭 완료")
            
            await page.wait_for_timeout(3000)
            print(f"🎉 매물번호 {property_number} 실제 업데이트 완료!")
            
            return True
            
        except Exception as e:
            print(f"❌ 실제 업데이트 중 오류: {e}")
            return False
    
    async def run_automation(self):
        """다중 매물 자동화 실행"""
        print("\n" + "="*80)
        print(f"🚀 다중 매물 자동화 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        if not self.property_numbers:
            print("❌ 처리할 매물번호가 없습니다.")
            return
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                page = await context.new_page()
                page.on('dialog', lambda dialog: dialog.accept())
                
                # 로그인
                login_success = await self.login(page)
                if not login_success:
                    print("❌ 로그인 실패로 자동화 중단")
                    return
                
                # 각 매물 순차 처리
                success_count = 0
                failed_properties = []
                
                for i, property_number in enumerate(self.property_numbers, 1):
                    success = await self.process_single_property(page, property_number, i, len(self.property_numbers))
                    
                    if success:
                        success_count += 1
                    else:
                        failed_properties.append(property_number)
                    
                    # 매물 간 대기
                    if i < len(self.property_numbers):
                        print(f"⏳ 다음 매물 처리까지 5초 대기...")
                        await page.wait_for_timeout(5000)
                
                # 🔄 실패한 매물 재시도 로직
                if failed_properties:
                    print(f"\n🔄 실패한 {len(failed_properties)}개 매물 재시도 중...")
                    print("="*60)
                    
                    retry_failed = []
                    for i, property_number in enumerate(failed_properties, 1):
                        print(f"\n[재시도 {i}/{len(failed_properties)}] 매물번호 {property_number}")
                        success = await self.process_single_property(page, property_number, i, len(failed_properties), retry=True)
                        
                        if success:
                            success_count += 1
                            print(f"✅ 재시도 성공: {property_number}")
                        else:
                            retry_failed.append(property_number)
                            print(f"❌ 재시도 실패: {property_number}")
                        
                        # 재시도 간 대기
                        if i < len(failed_properties):
                            await page.wait_for_timeout(3000)
                
                # 최종 결과
                print("\n" + "="*80)
                print("📊 다중 매물 자동화 완료!")
                print(f"✅ 최종 성공: {success_count}/{len(self.property_numbers)}개")
                if retry_failed:
                    print(f"❌ 최종 실패: {', '.join(retry_failed)}")
                else:
                    print("🎉 모든 매물 처리 완료!")
                print("="*80)
                
                # 최종 스크린샷
                screenshot_path = f"multi_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=screenshot_path)
                print(f"📸 최종 스크린샷: {screenshot_path}")
                
                await browser.close()
                
            except Exception as e:
                print(f"❌ 자동화 실행 실패: {e}")
                try:
                    await browser.close()
                except:
                    pass

async def main():
    """메인 실행 함수"""
    try:
        automation = MultiPropertyAutomation()
        await automation.run_automation()
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        print("💡 GitHub 저장소의 Settings → Secrets에서 LOGIN_ID, LOGIN_PASSWORD를 설정해주세요.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
