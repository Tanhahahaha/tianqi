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
    div_conMidtab = soup.find("div", class_="conMidtab3")
    tables = div_conMidtab.find_all("table")

    found_city = False
    for table_index, table in enumerate(tables):
        print(f"Table {table_index}:")
        trs = table.find_all("tr")
        if len(trs) > 0:
            first_td = trs[0].find_all("td")[0]
            if first_td.get_text(strip=True) == "宝安":
                found_city = True
                print(f"找到目标城市表格: {first_td.get_text(strip=True)}")
                for tr_index, tr in enumerate(trs):
                    print(f"  Row {tr_index}:")
                    tds = tr.find_all("td")
                    for td_index, td in enumerate(tds):
                        print(f"    TD {td_index}: {td.get_text(strip=True)}")

                    if len(tds) < 9:  # 跳过不完整的数据行
                        continue

                    # 获取区县名
                    city_td = tds[0] if 'rowsPan' in tds[0].get('class', []) else tds[1]
                    this_city = list(city_td.stripped_strings)[0]
                    print(f"    当前城市: {this_city}")  # 调试信息

                    if this_city == my_city:
                        found_city = True
                        print(f"找到城市: {this_city}")  # 调试信息

                        # 获取白天天气和夜间天气信息
                        weather_day = list(tds[2].stripped_strings())[0]
                        wind_day = list(tds[3].stripped_strings())[0] + list(tds[3].find('span', class_='conMidtabright').stripped_strings())[0]
                        high_temp = list(tds[4].stripped_strings())[0]

                        weather_night = list(tds[5].stripped_strings())[0]
                        wind_night = list(tds[6].stripped_strings())[0] + list(tds[6].find('span', class_='conMidtabright').stripped_strings())[0]
                        low_temp = list(tds[7].stripped_strings())[0]

                        temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                        weather_typ = weather_day if weather_day != "-" else weather_night
                        wind = f"{wind_day}" if wind_day != "--" else f"{wind_night}"

                        print(f"天气信息: {this_city}, {temp}, {weather_typ}, {wind}")  # 调试信息

                        return this_city, temp, weather_typ, wind

    if not found_city:
        print(f"未找到城市: {my_city}")  # 调试信息
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
    weather_report("宝安")
