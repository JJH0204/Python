import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import requests

# msedgedriver 경로 설정
EDGE_DRIVER_PATH = '/Users/krjaeh0/Downloads/edgedriver_mac64_m1/msedgedriver'

# Edge 드라이버 초기화
def init_edge_driver():
    service = Service(EDGE_DRIVER_PATH)
    options = webdriver.EdgeOptions()
    # options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    driver = webdriver.Edge(service=service, options=options)
    return driver

# 리그 오브 레전드 챔피언 이미지 크롤링 함수
def crawl_champion_images():
    driver = init_edge_driver()
    url = 'https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C'
    driver.get(url)

    time.sleep(3)  # 페이지 로딩 대기

    # dl 태그에 클래스가 JZn7KAqG인 요소를 찾기
    dl_elements = driver.find_elements("xpath", "//dl[@class='JZn7KAqG']")

    image_urls = []

    # dl 태그에 클래스가 JZn7KAqG인 요소에서 하위 요소인 모든 이미지 태그의 클래스 "VCEKqrfb" 설정이 된 요소의 src 속성 추출
    for dl in dl_elements:
        images = dl.find_elements("xpath", ".//img[@class='VCEKqrfb']")
        for img in images:
            src = img.get_attribute('src')
            # src 속성 중 .webp 로 끝나는 것만 추출
            if src.endswith('.webp'):
                image_urls.append(src)
    
    driver.quit()

    # 결과 출력 및 파일 저장
    for idx, image_url in enumerate(image_urls):
        if image_url:  # URL이 None이 아닌 경우에만 처리
            print(f'챔피언 {idx + 1}: {image_url}')
            try:
                save_path = f'champion_{idx + 1}.jpg'
                download_image(image_url, save_path)
            except Exception as e:
                print(f'이미지 다운로드 실패: {e}')

def download_image(image_url, save_path):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # HTTP 요청 성공 여부 확인

        # 이미지 데이터를 파일로 저장
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"이미지 다운로드 성공: {save_path}")
    except Exception as e:
        print(f"이미지 다운로드 실패: {e}")

if __name__ == '__main__':
    crawl_champion_images()