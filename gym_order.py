import datetime
import requests
import time
from lxml import etree
import sys
import smtplib
from email.mime.text import MIMEText

# 目标时间：周日、周一、周三、周四约第二天：18：00 - 19：00  #crontab: 55 10 * * 0,1,2,3,4
#         周二约第二天： 19：00 - 20：00

# 1. 使用cookie模拟登录home，添加date
# 2.根据时间找到相应课程，进入新的页面，获取data字典
# 3.post order url 确定预约。

today=datetime.date.today()
home_url="https://www.styd.cn"
course_oder_url=""
course_oder_date=""
course_oder_time=""
course_oder_base="科技园B1 下沉广场"

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
}
cookie="cookies.txt"
stop_duration=300

if today.weekday() == 2:
    target_time="19:00"
else:
    target_time="18:00"
# print(today.weekday(),target_time)

mail_receiver=""

def check_stop(start):
    now=datetime.datetime.now()
    if (now-start).seconds > int(stop_duration):
        return False
    else:
        return True

def set_cookie(cookie):
    global headers
    cookie=sys.path[0]+"/"+cookie
    with open(cookie,"r") as file:
        content=file.readline()
    if content:
        headers["Cookie"]=content
        return headers
    else:
        print("[ERROR]: cookies not define, please set cookie in ./cookies ")
        sys.exit(1)

def Date_url():

    today=datetime.date.today()
    nextday=next_day(today)
    prefix="/m/ad285710/default"
    date_url=home_url+prefix+"/search?date={}&shop_id=513773222&type=1".format(nextday)
    return date_url

def next_day(end):
    end=str(end)
    date=str(datetime.datetime.strptime(end,'%Y-%m-%d')+datetime.timedelta(days=1)).split(" ")[0]
    date=date.split("-")[0]+"-"+date.split("-")[1]+"-{}".format(int(date.split("-")[2]))
    return date

def get_url(url, headers):
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        print("[SUCCESS]: %s get ok" % (url))
        # print(response.text)
        return response
    else:
        print("[ERROR]: %s get failed" % (url))
        print("status code: {}".format(response.status_code))
        return None

def check_login():
    login_str="欢迎您"
    login_url="https://www.styd.cn/m/ad285710/user/default"
    response=get_url(login_url,headers).text
    # print(response)
    if login_str in response:
        print("[SUCCESS]: login success")
        return True
    else:
        print("[ERROR]: login failed")
        return False


def check_time(course_time):
    begin_time=course_time.split("-")[0].strip(" ")
    end_time=course_time.split("-")[1].strip(" ")
    begin=time.strptime(str(begin_time),"%H:%M")
    end=time.strptime(str(end_time),"%H:%M")
    target=time.strptime(target_time,"%H:%M")
    if target >= begin and target < end:
        return True
    else:
        return False

def check_status(status):
    if int(status.split("/")[0]) < int(status.split("/")[1]):
        return True
    else:
        return False


def get_course():

    global course_oder_url
    global course_oder_time
    global course_oder_date

    resp=get_url(Date_url(),headers)
    resp_dict=resp.json()
    resp_html=resp_dict["data"]["class_list"]
    html=etree.HTML(resp_html)
    path=html.xpath('//ul/li[@class="item_class_li  item_coach_8561796 "]/a')
    if path:
        for i in path:
            course_time=i.xpath('./div[@class="course_detail"]/p[@class="date"]/b/text()')[0].strip("\n").strip(" ")
            course_status=i.xpath('./div[@class="course_thumbs team"]/span/text()')[0].strip("\n").strip(" ")
            course_url=i.xpath('@href')[0].strip("\n").strip(" ")
            # course_base=i.xpath('./div[@class="course_detail"]/p[@class="name"]/text()')[0].strip("\n").strip(" ")
            if check_time(course_time):
                if check_status(course_status):
                    course_oder_url=home_url+course_url
                    course_oder_date=next_day(today)
                    course_oder_time=course_time
                    return False
                else:
                    print("[ERROR]: course is full !")
                    print("target date:{}, time:{}, status:{}".format(next_day(today),course_time,course_status))
                    send_email("健身房预订失败",mail_receiver,"<p>健身房预订失败，课程已满！</p><p>预订日期: {} 时间: {} 状态: {}</p>".format(next_day(today),course_time,course_status))
                    return False
            else:
                continue
    else:
        print("[ERROR]: course not open!")
        print("target date: {}".format(next_day(today)))
        send_email("健身房预订失败",mail_receiver,"<p>健身房预订失败，未开课！</p><p>预订日期: {}</p>".format(next_day(today)))
        return False
    return True

def get_order_data(course_url):

    resp=get_url(course_url,headers)
    resp_html=resp.text
    html=etree.HTML(resp_html)
    cat_id=html.xpath('//*[@id="card_12202342"]/@cat_id')[0]
    card_id=html.xpath('//*[@id="current_card"]/@card_id')[0]
    course_id=html.xpath('//*[@id="course_id"]/@value')[0]
    class_id=html.xpath('//*[@id="class_id"]/@value')[0]
    # class_type=html.xpath('//*[@id="class_type"]/@value')[0]
    time_from_stamp=html.xpath('//*[@id="time_from_stamp"]/@value')[0]
    time_to_stamp=html.xpath('//*[@id="time_to_stamp"]/@value')[0]
    is_waiting=html.xpath('//*[@id="is_waiting"]/@value')[0]
    quantity=1
    note=""
    data={"member_card_id": card_id,
        "card_cat_id": cat_id,  
        "course_id": course_id,
        "class_id": class_id, 
        "note":note,
        "time_from_stamp": time_from_stamp,
        "time_to_stamp": time_to_stamp,
        "quantity": quantity,
        "is_waiting":is_waiting
    }
    # print(cat_id,card_id,course_id,class_id,class_type,time_from_stamp,time_to_stamp,is_waiting,quantity,note)
    return data

def order_course(data):

    order_url="https://www.styd.cn/m/ad285710/course/order_confirm"
    response=requests.post(headers=headers,url=order_url,data=data)
    if response.status_code == 200:
        print("[SUCCESS]: %s order ok" % (order_url))
        # print(response.text)
        return True
    else:
        print("[ERROR]: %s order failed" % (order_url))
        print("status code: {}".format(response.status_code))
        return False

def send_email(subject,receiver,body):

    smtpserver = "" # smtp.xxx.com
    sender = ""
    psw = ""
    receiver = receiver

    if sender == "" or psw == "" or smtpserver == "" or receiver == "" :
        print("[WARNING]: send_email function not enable")
        return
    else:
        subject = subject
        body = body
        msg = MIMEText(body, 'html', 'utf-8')
        msg['from'] = sender
        msg['to'] = receiver
        msg['subject'] = subject

        print("sending email to {}...".format(receiver))
        smtp = smtplib.SMTP()
        smtp.connect(host=smtpserver)
        smtp.login(user=sender, password=psw)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()


def main():

    set_cookie(cookie)
    now=datetime.datetime.now()
    if check_login():
        while(get_course()):
            if check_stop(now):
                time.sleep(1)
            else:
                print("[ERROR]: get failed: get time > 5 mins")
                send_email("健身房预订失败",mail_receiver,"<p>健身房预订失败，超时！</p><p>get timeout > s{}</p>".format(stop_duration))
                sys.exit(1)

        if course_oder_url !="":
            data=get_order_data(course_oder_url)
            if order_course(data):
                print("[SUCCESS]: order successfully")
                print("date: {} time: {} base: {}".format(course_oder_date,course_oder_time,course_oder_base))
                send_email("健身房预订成功",mail_receiver,"<p>健身房预订成功，课程日期: {} 时间: {} 地点: {}</p>".format(course_oder_date,course_oder_time,course_oder_base))
                sys.exit(0)
            else:
                print("[ERROR]: order failed!  order_course post failed")
                send_email("健身房预订失败",mail_receiver,"<p>健身房预订失败，预订post请求失败！</p>")
                sys.exit(1)
        else:
            print("[ERROR]: order failed!  get_course get failed")
            sys.exit(1)
    else:
        print("[ERROR]: login failed!")
        send_email("健身房登录失败",mail_receiver,"<p>健身房登录失败，请重新登录</p>")
        sys.exit(1)

if __name__=="__main__":
    main()
