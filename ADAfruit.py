import time
import Adafruit_ADS1x15
# ADS1015の設定をします
ads = Adafruit_ADS1x15.ADS1015(address=0x68, busnum=1)

# ゲインの設定です
# 指定によって、取得できる電圧の範囲が変わります

#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
GAIN = 1

#
#「ゲイン1」の時の、「受信データ1単位」の電圧を計算します
#

# 「ゲイン1」の範囲はプラス・マイナス 4.096なので、8.192になります
RANGE = 4.096 * 2

# ADSは上記範囲を12bit(4096)で表すので、上記範囲を4096で割ると
# ADSのデータ「1」につき、電圧は0.002[V]になります。
# UNIT=単位
UNIT = RANGE / 4096

# ループを100回繰り返します
for i in range(100):

    # ADSのアナログ入力ピンを指定します
    ads1015_pin  = 0

    data = 0
    volt = 0

    # ADS1015からデータを取得します
    data = ads.read_adc( ads1015_pin, gain=GAIN)

    # 取得データから電圧を計算します
    volt = data * UNIT

    print("受信データ：" + str(data))
    print("電圧      ：" + "{:.3f}".format(volt))

    # 1秒待機します
    time.sleep(1)

print("done.")