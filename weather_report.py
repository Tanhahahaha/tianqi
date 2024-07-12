# 安装依赖 pip3 install requests html5lib bs4 schedule
import os
import requests
import json
from bs4 import BeautifulSoup

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号
openId = os.environ.get("OPEN_ID")
# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID")

def get_weather(my_city):
    url = "http://www.weather.com.cn/textFC/guangdong.shtml"
    resp = requests.get(url)
    text = resp.content.decode("utf-8")
    soup = BeautifulSoup(text, 'html5lib')
    div_conMidtab = soup.find("div", class_="conMidtab")
    tables = div_conMidtab.find_all("table")

    # 打印每个 table 的数据
    for table_index, table in enumerate(tables):
        print(f"Table {table_index}:\n{table}")

    for table in tables:
        trs = table.find_all("tr")[2:]
        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) < 8:  # 跳过不完整的数据行
                continue

            city_td = tds[0] if tds[0].get('class') == ['rowsPan'] else tds[1]
            this_city = list(city_td.stripped_strings)[0]
            if this_city == my_city:
                high_temp_td = tds[-5]
                low_temp_td = tds[-2]
                weather_type_day_td = tds[-7]
                weather_type_night_td = tds[-4]
                wind_td_day = tds[-6]
                wind_td_day_night = tds[-3]

                high_temp = list(high_temp_td.stripped_strings)[0]
                low_temp = list(low_temp_td.stripped_strings())[0]
                weather_typ_day = list(weather_type_day_td.stripped_strings())[0]
                weather_type_night = list(weather_type_night_td.stripped_strings())[0]

                wind_day = list(wind_td_day.stripped_strings())[0] + list(wind_td_day.stripped_strings())[1]
                wind_night = list(wind_td_day_night.stripped_strings())[0] + list(wind_td_day_night.stripped_strings())[1]

                temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                wind = f"{wind_day}" if wind_day != "--" else f"{wind_night}"
                return this_city, temp, weather_typ, wind
    return None

def get_access_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    access_token = response.get('access_token')
    return access_token

def get_daily_love():
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love

def send_weather(access_token, weather):
    if weather is None:
        print("未能获取天气信息，不发送通知。")
        return

    if "雨" not in weather[2]:
        print(f"天气不是雨天，不发送通知。天气信息：{weather[2]}")
        return

    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")

    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {
                "value": today_str
            },
            "region": {
                "value": weather[0]
            },
            "weather": {
                "value": weather[2]
            },
            "temp": {
                "value": weather[1]
            },
            "wind_dir": {
                "value": weather[3]
            },
            "today_note": {
                "value": get_daily_love()
            }
        }
    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)

def weather_report(this_city):
    access_token = get_access_token()
    weather = get_weather(this_city)
    print(f"天气信息： {weather}")
    send_weather(access_token, weather)

if __name__ == '__main__':
    weather_report("深圳")
