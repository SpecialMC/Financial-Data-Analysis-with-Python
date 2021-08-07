#사전준비
# 파이낸스 데이터리더와 맷플롯립을 임포트
import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates



#종목번호와 시작날짜 입력
df = fdr.DataReader('006650', '2020-04-01')



# 1번 창) 26주 지수 이동평균(EMA 130)
#26주 지수 이동평균 구하기
ema60 = df.Close.ewm(span=60).mean()   # ① 종가의 12주 지수 이동평균 (평일 5일 x 12 = 60)
ema130 = df.Close.ewm(span=130).mean() # ② 종가의 26주 지수 이동평균
#df에 합친 후 ohlc 데이터 프레임에 필요한 것만 넣기
df = df.assign(ema130=ema130, ema60=ema60).dropna() 
df['number'] = df.index.map(mdates.date2num)  # ⑥그래프 x축에 날짜를 표시하기 위해 (날짜 정보를 담고 있는 숫자를)열로 추가함
ohlc = df[['number','Open','High','Low','Close']]



#2번 창) 오실리테이터: 스토캐스틱
# ①
# 14일 동안의 최댓값을 구한다.
# min_periods=1은 14일 기간에 해당하는 데이터가 모두 누적되지 않아도
# 최소 기간인 1일 이상의 데이터만 존재하면 최댓값을 구하라는 의미다.
ndays_high = df.High.rolling(window=14, min_periods=1).max()
# ② ①과 동일하지만 최댓값이 아닌 최솟값을 구하는 것만 다르다.
ndays_low = df.Low.rolling(window=14, min_periods=1).min()
# ③ %K
fast_k = (df.Close - ndays_low) / (ndays_high - ndays_low) * 100
# ④ %D
slow_d= fast_k.rolling(window=3).mean()               
# ⑤ %K와 %D로부터 데이터프레임 생성 후 결측값 제거
df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()



#그래프로 표현
plt.figure(figsize=(20, 25))
p1 = plt.subplot(3, 1, 1)
plt.title('Company Name')
plt.grid(True)
candlestick_ohlc(p1, ohlc.values, width=.6, colorup='red', colordown='blue')
p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['ema130'], color='c', label='EMA130')
for i in range(1, len(df.Close)):
    # 130일 이동 지수 평균이 상승하고 %D가 20 아래로 떨어지면
    if df.ema130.values[i-1] < df.ema130.values[i] and \
        df.slow_d.values[i-1] >= 20 and df.slow_d.values[i] < 20:
        # 빨간색 삼각형으로 매수 신호 표시
        plt.plot(df.number.values[i], 0, 'r^')

    # 130일 이동 지수 평균이 하락하고 %D가 80 위로 상승하면
    elif df.ema130.values[i-1] > df.ema130.values[i] and \
        df.slow_d.values[i-1] <= 80 and df.slow_d.values[i] > 80:
        # 파란색 삼각형으로 매도 신호 표시
        plt.plot(df.number.values[i], 0, 'bv') 
plt.legend(loc='best')

p2 = plt.subplot(3, 1, 2)
plt.grid(True)
p2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['slow_d'], color='k', label='%D')
plt.yticks([0, 20, 80, 100])
plt.legend(loc='best')
plt.show()