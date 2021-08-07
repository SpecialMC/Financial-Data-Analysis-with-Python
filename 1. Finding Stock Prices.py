#<사전준비>
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
from matplotlib import dates as mdates
import matplotlib.pyplot as plt
import requests



#<종목코드 불러오기>
#상장된 회사 정보가 담긴 테이블을 데이터프레임으로 불러오기
dfstockcode = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
#테이블이 어떤 정보를 담고 있는지 확인하기
dfstockcode.info()
#종목코드를 6자리 숫자로 맞춰주기
dfstockcode.종목코드 = dfstockcode.종목코드.map('{:06d}'.format)
#회사명을 넣으면 종목코드가 나오는 딕셔너리 만들기 ()
stock_to_code = dict(zip(dfstockcode.회사명, dfstockcode.종목코드))
stock_to_code['삼성전자']


#<종목 종가 추출하기>
#종목코드 6자리를 넣어 url 설정하기
url = 'https://finance.naver.com/item/sise_day.nhn?code=068270&page=1'
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
response = requests.get(url, headers=headers)
#df라는 pandas 데이터프레임 생성
df = pd.DataFrame()
sise_url = url[:55]
#100페이지까지 종가 추출
for page in range(1, 101):
    page_url = '{}&page={}'.format(sise_url, page)
    print(page_url)
    # URL에서 종가 테이블을 데이터프레임으로 추출하여 table 변수에 저장
    response = requests.get(page_url, headers=headers)
    html = bs(response.text, 'html.parser')
    html_table = html.select("table")
    table = pd.read_html(str(html_table))
    # 얻은 데이터프레임을 df 데이터프레임에 누적 (결측값 제거 후)
    df = df.append(table[0].dropna())