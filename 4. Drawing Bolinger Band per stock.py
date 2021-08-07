#사전준비
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime



#저장명을 위해 오늘 날짜 가져오기
now = datetime.datetime.now()
nowDate = now.strftime('%Y-%m-%d')



#현존하는 종목 코드를 리스트로 저장하기
#엑셀 파일을 데이터프레임에 저장하기
mydata = pd.read_excel('stock data.xlsx')
#단축코드만 저장하기
mydata = mydata['단축코드']
#리스트로 변환하기
mydata = mydata.tolist()
#원하는 범위까지만 추출하기
stocklist = mydata[1:2]



#종목코드로부터 회사명을 도출하기
#상장된 회사 정보가 담긴 테이블을 데이터프레임으로 불러오기
dfstockcode = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
#종목코드를 6자리 숫자로 맞춰주기
dfstockcode.종목코드 = dfstockcode.종목코드.map('{:06d}'.format)
#회사명을 넣으면 종목코드가 나오는 딕셔너리 만들기 ()
code_to_stock = dict(zip(dfstockcode.종목코드, dfstockcode.회사명))
#원하는 종목코드 추출하기
code_to_stock['002460']


#범위에 대해 분석차트 반환
for i in stocklist:
      dfstockcode = format(i, '06')
      print(dfstockcode)
      
      #기간을 정해 회사의 주가 정보를 불러온다
      df = fdr.DataReader(dfstockcode, '2021-01-01')
      
      #20일 이동평균(중간 볼린저 밴드), 상하단 볼린저밴드, %b를 구한다
      df['MA20'] = df['Close'].rolling(window=20).mean()
      df['stddev'] = df['Close'].rolling(window=20).std() 
      df['upper'] = df['MA20'] + (df['stddev'] * 2)
      df['lower'] = df['MA20'] - (df['stddev'] * 2)
      df['PB'] = (df['Close'] - df['lower']) / (df['upper'] - df['lower'])
      
      # 고가, 저가, 종가의 합을 3으로 나눠서 중심 가격 TP(Typical Price)를 구한다.
      df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
      df['PMF'] = 0
      df['NMF'] = 0
      
      # range 함수는 마지막 값을 포함하지 않으므로 0부터 종가개수 -2까지 반복
      for i in range(len(df.Close)-1):
          # i번째 중심 가격보다 i+1번째 중심 가격이 높으면
          if df.TP.values[i] < df.TP.values[i+1]:
              # i+1번째 중심 가격과 i+1번째 거래량의 곱을
              # # # i+1번째 긍정적 현금 흐름 PMF(Positive Money Flow)에 저장
              df.PMF.values[i+1] = df.TP.values[i+1] * df.Volume.values[i+1]
              # i+1번째 부정적 현금 흐름 NMF(Negative Money Flow)값은 0으로 저장
              df.NMF.values[i+1] = 0
      else:
          # 반대의 경우에는 NMF를 계산하고
          df.NMF.values[i+1] = df.TP.values[i+1] * df.Volume.values[i+1]
          # PFM의 값은 0으로 저장
          df.PMF.values[i+1] = 0

      # 10일 동안의 긍정적 현금 흐름의 합을 10일 동안의 부정적 현금 흐름의 합으로 나눈 결과를 MFR(Money Flow Ratio) 열에 저장
      df['MFR'] = (df.PMF.rolling(window=10).sum() / df.NMF.rolling(window=10).sum())
      # 10일 기준으로 현금 흐름 지수를 계산한 결과를 MFI10(Money Flow Index 10)열에 저장
      # # MFI = 100 - (100 / (1+긍정적 현금 흐름 / 부정적 현금흐름))
      df['MFI10'] = 100 - 100 / (1 + df['MFR'])
    
      # 볼린저밴드와 매수시점, 매도시점을 나타내는 그래프 시각화
      plt.figure(figsize=(24, 20))
      plt.subplot(2, 1, 1)
      plt.title(dfstockcode + 'Bollinger Band(20 day, 2 std) - Trend Following')
      plt.plot(df.index, df['Close'], color='#0000ff', label='Close')
      plt.plot(df.index, df['upper'], 'r--', label ='Upper band')
      plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
      plt.plot(df.index, df['lower'], 'c--', label ='Lower band')
      plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')

      for i in range(len(df.Close)):
          # %b가 0.8보다 크고 10일 기준 MFI가 80보다 크면
          if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:
              # 매수 시점을 나타내기 위해 첫 번째 그래프의 종가 위치에 빨간색 삼각형을 표시
              plt.plot(df.index.values[i], df.Close.values[i], 'r^')

          # %b가 0.2보다 작고 10일 기준 MFI가 20보다 작으면
          elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:
              # 매도 시점을 나타내기 위해 첫 번째 그래프의 종가 위치에 파란색 삼각형을 표시 
              plt.plot(df.index.values[i], df.Close.values[i], 'bv')

      plt.legend(loc='best')
      plt.savefig(code_to_stock[dfstockcode] + ' - ' + dfstockcode + ' ('+ nowDate + ').png')



