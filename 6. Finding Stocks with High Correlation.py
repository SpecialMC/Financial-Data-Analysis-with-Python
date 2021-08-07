#사전준비
from sklearn.preprocessing import Normalizer
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt



#종목별 종가 전처리하기
#상장된 회사 정보가 담긴 테이블을 데이터프레임으로 불러오기
dfstockcode = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
#종목코드를 6자리 숫자로 맞춰주기
dfstockcode.종목코드 = dfstockcode.종목코드.map('{:06d}'.format)
#종목코드만 추출하기
dfstockcode = dfstockcode['종목코드']
#리스트로 변환하기
dfstockcode = dfstockcode.tolist()

#적당한 범위만 넣기
mydata = dfstockcode

#모든 종목에 대해 2020년1월1일부터의 종가를 불러온다
prices_list = []
for code in mydata:
    try:
        prices = fdr.DataReader(code, '01/01/2021')['Close']
        prices = pd.DataFrame(prices)
        prices.columns = [code]
        prices_list.append(prices)
    except:
        pass
    prices_df = pd.concat(prices_list,axis=1)

prices_df.sort_index(inplace=True)



#변화율 구해 넣기
#pct_change()를 통해 변화율을 구해 df에 넣기
df = prices_df.pct_change().iloc[1:]
df.info()

#널값은 0으로 채우기
df = df.fillna(0)
df.info()

#변화율의 범위를 (-1, 1)로 정규화하기
normalize = Normalizer()
array_norm = normalize.fit_transform(df)
df_norm = pd.DataFrame(array_norm, columns=df.columns)
df = df_norm.set_index(df.index)



#상관관계 구하기
#상관관계를 구하고 싶은 대상종목번호 지정하기
my_code = "001230"

#상관관계가 0.4보다 높은 종목 추출
for code in mydata:
    if df[my_code].corr(df[code]) > 0.6:
        corr = df[my_code].corr(df[code])
        print(my_code + ' & ' + code +'=')
        print(corr)



#<종가 그래프를 그려 두 종목의 움직임 비교해보기>
#2020년 1월 2일을 기준점으로 잡아 종가 변동률을 데이터프레임으로 넣기
A = (prices_df['002460'] / prices_df['002460'].loc['2021-01-04']) * 100
B = (prices_df['001230'] / prices_df['001230'].loc['2021-01-04']) * 100

#그래프로 시각화하기
graph_df = pd.concat([A, B], axis=1)
graph_df.plot()
plt.show()