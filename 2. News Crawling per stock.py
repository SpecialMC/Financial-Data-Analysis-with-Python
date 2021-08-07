#<사전준비>
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os
from newspaper import Article


#<종목코드 찾기>
#상장된 회사 정보가 담긴 테이블을 데이터프레임으로 불러오기
dfstockcode = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
#종목코드를 6자리 숫자로 맞춰주기
dfstockcode.종목코드 = dfstockcode.종목코드.map('{:06d}'.format)
#회사명을 넣으면 종목코드가 나오는 딕셔너리 만들기 ()
stock_to_code = dict(zip(dfstockcode.회사명, dfstockcode.종목코드))
#원하는 종목코드 추출하기
stock_to_code['화성산업']



#<종목별 뉴스제목, URL 크롤링>
#기사제목과 URL을 반환하는 함수 만들기
def crawler(company_name, maxpage):
    df_result = None
    
    page = 1
    company_code = stock_to_code[company_name]

    # 1페이지부터 maxpage의 페이지까지
    while page <= int(maxpage): 
    
        #URL구조를 텍스트로 가져오기
        url = 'https://finance.naver.com/item/news_news.nhn?code=' + str(company_code) + '&page=' + str(page) 
        source_code = requests.get(url).text
        html = BeautifulSoup(source_code, "lxml") 
 
        # 뉴스 제목을 title_result라는 리스트에 쌓기
        titles = html.select('.title')
        title_result=[]
        for title in titles: 
            title = title.get_text() 
            title = re.sub('\n','',title)
            title_result.append(title)
 
        # 뉴스 링크를 link_result라는 리스트에 쌓기
        links = html.select('.title') 
        link_result =[]
        for link in links: 
            add = 'https://finance.naver.com' + link.find('a')['href']
            link_result.append(add)\
 
        # 두 리스트를 result라는 데이터프레임으로 합쳐 csv파일로 저장하기 
        result= {"기사제목" : title_result, "링크" : link_result} 
        df_temp = pd.DataFrame(result)
        
        # for문 내에서 데이터프레임이 만들어질 때마다 이전 데이터프레임과 결합
        if df_result is not None:
          df_result = pd.concat([df_result, df_temp])
        else:
          df_result = df_temp
        
        print(page,"페이지 진행 중입니다.")
 
        page += 1
    return df_result

#회사명, 페이지를 넣어 기사제목과 링크 크롤링하기!
df_result = crawler('화성산업', 13)
df_result



#<종목별 뉴스 내용까지 크롤링>
#URL을 넣으면 기사를 추출하는 함수 생성
def url_to_text(url):
  article = Article(url, language='ko')
  article.download()
  article.parse()
  return article.text
df_result['본문'] = df_result['링크'].apply(url_to_text)
#잘 가져왔는지 확인
df_result
#csv 파일로 저장하기
df_result.to_csv('화성산업 뉴스.csv', index=False, encoding='utf-8-sig')



#<워드클라우드는 COLAB에서 진행하세요>
#명사만 추출하는 함수 지정
https://colab.research.google.com/drive/1ELg5pc6QNGUwkbF9TpopQfOvwQbizqPk