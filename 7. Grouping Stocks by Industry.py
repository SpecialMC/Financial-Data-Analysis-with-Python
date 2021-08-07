#사전준비
import FinanceDataReader as fdr
import pandas as pd
from tabulate import tabulate


#<같은 산업군의 종목 리스트 불러오기>
#한국 상장 주식 데이터 불러오기
df_krx = fdr.StockListing('KRX')
#산업명이 없는 종목 없애기
df = df_krx.dropna(axis=0)
#산업군으로 분류하기
df.sort_values('Sector')
#종목코드를 넣으면 산업군이 나오는 딕셔너리 만들기
stock_to_sector = dict(zip(df.Symbol, df.Sector))
#종목번호를 넣어 산업군 확인하기
stock_to_sector['004020']

#산업군에 속한 종목 (tabulate로 예쁘게) 불러오기
print(tabulate(df[df['Sector'] == '1차 철강 제조업'], headers='keys', tablefmt='psql'))