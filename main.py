import time
from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import sys
import os
import random
from zhdate import ZhDate

############### 参数设定区域 #################
# 微信测试号信息
appID = ''
appsecret = ''
# 模板消息接口id
template1 = ''  # 自定义模板一的模板消息接口id号
template2 = ''  # 自定义模板二的模板消息接口id号，不启用不用填写
template3 = ''  # 自定义模板三的模板消息接口id号，不启用不用填写
template4 = ''  # 自定义模板四的模板消息接口id号，不启用不用填写
# 关注的成员ID，测试号页面的微信号，实则为账户的openID
user_id = ''
# 天行数据
key = ''
# 心知天气
zxkey = ''
# 高德key
gdkey = ''

# 生日日期参数填写
birthday = 'l-1-24'  # 格式 %month-%day 【用r-月份-日期格式填写，不要出现年份,r代表农历，其他字母代表公历】
# 相处开始日期
start_date = '2023-1-11'  # 使用年份-月份-日期的形式填写

location = 'qinhuangdao'  # 心知天气api 空气质量监测地区，英文拼写
cityacode = '130302'  # 高德地图天气情况获取，城市acode 参照readme文档填写

############### 参数设定区域结束 ##################

############## ↓ ↓ ↓ ↓ 下方程序根据需求自定义更改 ↓ ↓ ↓ ↓ ################
today = datetime.now()
# 当前日期获取
currentTime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
nowDate = time.strftime("%H:%M:%S", time.localtime(time.time()))
year = time.localtime().tm_year
month = time.localtime().tm_mon
day = time.localtime().tm_mday
today1 = datetime.date(datetime(year=year, month=month, day=day))


# 由于微信模板消息单个参数20字符限制，对请求数据分割
#### 逻辑：中文直接取20个字符，英文需要对句子使用split，才能判断词数
def zh_split(sentence):
    if len(sentence) <= 20:
        return sentence, '', ''
    elif len(sentence) <= 40:
        return sentence[0:19], sentence[19:], ''  # [0:19]表示索引包括0不包括19
    else:
        return sentence[0:19], sentence[19:39], sentence[39:]

# 英文分割,截取19个词
def en_split(sentence):
    sentence = sentence.split()
    if len(sentence) < 20:
        return ' '.join(sentence), '', ''
    elif len(sentence) < 38:
        return ' '.join(sentence[0:18]), ' '.join(sentence[18:]), ''
    else:
        return ' '.join(sentence[0:18]), ' '.join(sentence[18:37]), ' '.join(sentence[37:])

# 相处日期
#### 逻辑：从现在时间-相识时间得出时间长！
def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


### 逻辑: 判断生日是否已经过了，过了的话下一年的时间长计算，没过则用现在的月份日期-生日的月份日期
# 生日日期计算
# def get_birthday():
#     next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
#     if next < datetime.now():
#         next = next.replace(year=next.year + 1)
#     return (next - today).days

def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日(格式为r-2023-12-1)
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)

    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today1 > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today1)).split(" ")[0]
    elif today1 == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today1)).split(" ")[0]
    return birth_day


# 当前日期获取处理
def getweek():
    weekEng = time.strftime("%A", time.localtime(time.time()))
    week_list = {
        "Monday": "星期一",
        "Tuesday": "星期二",
        "Wednesday": "星期三",
        "Thursday": "星期四",
        "Friday": "星期五",
        "Saturday": "星期六",
        "Sunday": "星期日"
    }
    week = week_list[weekEng]
    return week


##### API调用部分开始 ###

# 高德
def citybase():
    url = 'https://restapi.amap.com/v3/weather/weatherInfo'
    params = {
        "key": gdkey,
        "city": cityacode,  # 城市acode码填写
        "extensions": "base",
    }
    resp = requests.get(url, params)
    data = resp.json()
    if resp.status_code == 200:
        return data
    else:
        print('请求失败，请查看错误')


def cityall():
    url = 'https://restapi.amap.com/v3/weather/weatherInfo'
    params = {
        "key": gdkey,
        "city": cityacode,  # 城市acode码填写
        "extensions": "all",
    }
    resp = requests.get(url, params)
    data = resp.json()
    if resp.status_code == 200:
        return data
    else:
        print('请求失败')


citybase = citybase()
cityall = cityall()
address = citybase['lives'][0]['city']  # 地点
weather = citybase['lives'][0]['weather']  # 天气
temperature = citybase['lives'][0]['temperature']  # 温度
winddirection = citybase['lives'][0]['winddirection']  # 风向
windpower = citybase['lives'][0]['windpower']  # 风力
dayweather = cityall['forecasts'][0]['casts'][0]['dayweather']
nightweather = cityall['forecasts'][0]['casts'][0]['nightweather']
daytemp = cityall['forecasts'][0]['casts'][0]['daytemp']
nighttemp = cityall['forecasts'][0]['casts'][0]['nighttemp']

print('--------', '\n', '城市:', address, '\n', '天气:', weather, '\n', '当下温度:', temperature + '℃', '\n', '风向:',
      winddirection, '\n', '风速:', windpower)
print('--------')
print(cityall['forecasts'][0]['casts'][0]['dayweather'])
print(cityall['forecasts'][0]['casts'][0]['nightweather'])
print(cityall['forecasts'][0]['casts'][0]['daytemp'])
print(cityall['forecasts'][0]['casts'][0]['nighttemp'])
print('--------')
print(cityall['forecasts'][0]['casts'][1]['dayweather'])
print(cityall['forecasts'][0]['casts'][1]['nightweather'])
print(cityall['forecasts'][0]['casts'][1]['daytemp'])
print(cityall['forecasts'][0]['casts'][1]['nighttemp'])


# 随机颜色渲染
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# 获取空气质量
def getkqzl():
    params = {
        "key": zxkey,
        "location": location,  # 查询地点设置为访问IP所在地
        "language": "zh-Hans",
        "unit": "c",
        "days": "1"
    }
    url = 'https://api.seniverse.com/v3/life/suggestion.json'
    resp = requests.get(url, params)
    if resp.status_code == 200:
        data = resp.json()["results"]
        return data[0]['suggestion'][0]['air_pollution']['brief']
    else:
        print('请求失败')


# 处理获取到的数据
getkqzl = getkqzl()
suggestion = getkqzl  # 空气质量


# 根据空气质量设置颜色
def suggestioncolor():
    if suggestion == '优':
        return '#33FF33'
    elif suggestion == '良' or suggestion == '中':
        return '#77FF00'
    else:
        return '#FFAA33'


# 土味情话
def getSayLove():
    url = 'http://api.tianapi.com/saylove/index?key='
    resp = requests.get(url + key)
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]['content']
    else:
        print('请求失败')


# 情诗
def getqingshi():
    url = 'http://api.tianapi.com/qingshi/index?key='
    resp = requests.get(url + key)
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]['content']
    else:
        print('请求失败')


# 早安心语
def getzaoan():
    url = 'http://api.tianapi.com/zaoan/index?key='
    resp = requests.get(url + key)
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]['content']
    else:
        print('请求失败')


# 晚安心语
def getwanan():
    url = 'http://api.tianapi.com/wanan/index?key='
    resp = requests.get(url + key)
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]['content']
    else:
        print('请求失败')


# 励志古言
def getlzmy():
    url = 'http://api.tianapi.com/lzmy/index?key='
    resp = requests.get(url + key)
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]
    else:
        print('请求失败')


# 彩虹屁
def getcaihongpi():
    url = 'http://api.tianapi.com/caihongpi/index?key='
    resp = requests.get(url + key)
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]['content']
    else:
        print('请求失败')


# 节假日
def getjiejiari():
    url = 'http://api.tianapi.com/jiejiari/index?key='
    resp = requests.get(url + key + '&date=' + currentTime + '&type=2')
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]
    else:
        print('请求失败')


# one一个
def getone():
    url = 'http://api.tianapi.com/one/index?key='
    resp = requests.get(url + key + '&rand=1')
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]['word']
    else:
        print('请求失败')


# 天气诗句
def gettianqishiju():
    url = 'http://api.tianapi.com/tianqishiju/index?key='
    weatherlist = {
        "风": "1",
        "云": "2",
        "雨": "3",
        "雪": "4",
        "霜": "5",
        "露": "6",
        "雾": "7",
        "雷": "8",
        "晴": "9",
        "阴": "10",
    }
    resp = requests.get(url + key + '&tqtype=' + weatherlist[weather])
    if resp.status_code == 200:
        data = resp.json()
        return data['newslist'][0]
    else:
        print('请求失败')


# 每日英语
def geteverydayEnglish():
    url = 'http://apis.tianapi.com/everyday/index?key='
    resp = requests.get(url + key)
    if resp.status_code == 200:
        data = resp.json()
        return data['result']
    else:
        print('请求失败')

getSayLove = getSayLove()
getSayLove1, getSayLove2, getSayLove3 = zh_split(getSayLove)
getqingshi = getqingshi()
getzaoan = getzaoan()
getwanan = getwanan()
getlzmy = getlzmy()
getcaihongpi = getcaihongpi()
getcaihongpi1, getcaihongpi2, getcaihongpi3 = zh_split(getcaihongpi)
getjiejiari = getjiejiari()
getone = getone()
# gettianqishiju = gettianqishiju()
geteverydayEnglish = geteverydayEnglish()
saying1, saying2, saying3 = zh_split(geteverydayEnglish['note'])
source1, source2, source3 = en_split(geteverydayEnglish['content'])
##### API调用部分结束 ###

# 推送消息
client = WeChatClient(appID, appsecret)
wm = WeChatMessage(client)

# if "06:00:00" < nowDate < "22:00:00":
#     # 微信消息模板 ID
#     template_id = template1
#     # 自定义的内容
#     data = {
#         "getSayLove": {"value": getSayLove, "color": get_random_color()},
#         "currentTime": {"value": currentTime, "color": get_random_color()},
#         "nongli": {"value": getjiejiari['lunarmonth'] + '-' + getjiejiari['lunarday'], "color": get_random_color()},
#         "week": {"value": getweek(), "color": get_random_color()},
#         "nowDate": {"value": nowDate, "color": get_random_color()},
#         "address": {"value": address, "color": get_random_color()},
#         "dayweather": {"value": dayweather, "color": get_random_color()},
#         "nightweather": {"value": nightweather, "color": get_random_color()},
#         "winddirection": {"value": winddirection, "color": get_random_color()},
#         "windpower": {"value": windpower, "color": get_random_color()},
#         "weather": {"value": weather, "color": get_random_color()},
#         "daytemp": {"value": daytemp, "color": get_random_color()},
#         "nighttemp": {"value": nighttemp, "color": get_random_color()},
#         "temperature": {"value": temperature + '℃', "color": get_random_color()},
#         "suggestion": {"value": suggestion, "color": suggestioncolor()},
#         "saying": {"value": getlzmy['saying'], "color": get_random_color()},
#         "source": {"value": getlzmy['source'], "color": get_random_color()},
#         "transl": {"value": getlzmy['transl'], "color": get_random_color()},
#         "get_birthday": {"value": get_birthday(), "color": get_random_color()},
#         "meeting": {"value": get_count(), "color": get_random_color()}, \
#         }

if "06:00:00" < nowDate < "22:00:00":
    template_id = template2
    data = {
        "getSayLove1": {"value": getSayLove1, "color": get_random_color()},
        "getSayLove2": {"value": getSayLove2, "color": get_random_color()},
        "getSayLove3": {"value": getSayLove3, "color": get_random_color()},
        "currentTime": {"value": currentTime, "color": get_random_color()},
        "nongli": {"value": getjiejiari['lunarmonth'] + '-' + getjiejiari['lunarday'], "color": get_random_color()},
        "week": {"value": getweek(), "color": get_random_color()},
        "dayweather": {"value": dayweather, "color": get_random_color()},
        "nightweather": {"value": nightweather, "color": get_random_color()},
        "winddirection": {"value": winddirection, "color": get_random_color()},
        "windpower": {"value": windpower, "color": get_random_color()},
        "weather": {"value": weather, "color": get_random_color()},
        "daytemp": {"value": daytemp, "color": get_random_color()},
        "nighttemp": {"value": nighttemp, "color": get_random_color()},
        "temperature": {"value": temperature + '℃', "color": get_random_color()},
        "suggestion": {"value": suggestion, "color": suggestioncolor()},
        "caihongpi1": {"value": getcaihongpi1, "color": get_random_color()},
        "caihongpi2": {"value": getcaihongpi2, "color": get_random_color()},
        "caihongpi3": {"value": getcaihongpi3, "color": get_random_color()},
        "saying1": {"value": saying1, "color": get_random_color()},
        "saying2": {"value": saying2, "color": get_random_color()},
        "saying3": {"value": saying3, "color": get_random_color()},
        "source1": {"value": source1, "color": get_random_color()},
        "source2": {"value": source2, "color": get_random_color()},
        "source3": {"value": source3, "color": get_random_color()},
        "get_birthday": {"value": get_birthday(birthday, year, today1), "color": get_random_color()},
        "meeting": {"value": get_count(), "color": get_random_color()}
    }
# if "14:00:00" < nowDate < "18:00:00":
#     template_id = template3
#     data = {
#         "nowDate": {"value": nowDate, "color": get_random_color()},
#         "week": {"value": getweek(), "color": get_random_color()},
#         "city": {"value": address, "color": get_random_color()},
#         "weather": {"value": weather, "color": get_random_color()},
#         "kqtype": {"value": suggestion, "color": suggestioncolor()},
#         "tem": {"value": temperature + '℃', "color": get_random_color()},
#     }
# if "18:00:00" < nowDate < "24:00:00":
#     template_id = template4
#     data = {
#         "nowDate": {"value": nowDate, "color": get_random_color()},
#         "week": {"value": getweek(), "color": get_random_color()},
#         "city": {"value": address, "color": get_random_color()},
#         "weather": {"value": weather, "color": get_random_color()},
#         "kqtype": {"value": suggestion, "color": suggestioncolor()},
#         "tem": {"value": temperature + '℃', "color": get_random_color()},
#     }


# 发送自定义参数集，请求微信api进行处理，改成模板形式进行请求
resp = wm.send_template(user_id, template_id, data, 'https://yang-yang-no-1.github.io/')
print(resp)
print(data)
######## 下方是可获取api信息的显示，如有需要可以打开进行查看 #######

print("当前时间：", currentTime, '-', nowDate, '-', getweek())
print('位置天气：', address, '-', temperature + '℃', '-', weather, '-', suggestion)
print('土味情话', getSayLove)
print('情诗', getqingshi)
print('早安', getzaoan)
print('晚安', getwanan)
print('励志名言', getlzmy['saying'], '-', getlzmy['source'], '-', getlzmy['transl'])
print('彩虹屁', getcaihongpi)
print('节假日', getjiejiari['lunarmonth'], '-', getjiejiari['lunarday'], getjiejiari['info'])
print('one', getone)
print('每日英语', geteverydayEnglish)
# print(weather, '-', gettianqishiju['source'], '-', gettianqishiju['author'], '-', gettianqishiju['content'])
