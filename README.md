# gym_order
> auto order gym in specific time

> 自动运行预定健身房脚本，可以指定时间，日期，地点，并可选通过邮件通知

## 使用方法:
> Ubuntu16.04为例
### 1.下载代码
    git clone https://github.com/WSure00/gym_order.git
### 2.写入cookie，用来登录健身房网站。写入到./cookies.txt
    modify your cookie in ./cookies.txt
### 3.添加你想预约的时间，在 gym_order.py 中修改变量 {target_time}
    modify your expect time {target_time} in gym_order.py 
### 4.可选操作: 在 gym_order.py文件中添加邮件通知变量的：{mail_receiver},{smtpserver},{sender},{psw} (邮件通知可选)
    set your own vars in gym_order.py: {mail_receiver},{smtpserver},{sender},{psw}
    
    ps:function send email is optional
 效果如图：
 <img src="https://raw.githubusercontent.com/WSure00/gym_order_auto/main/src/images/email_result.png" width="200px" alt="邮件效果图" align="middle"/>
    
### 5.可选操作: 在Linux中可以设置crontab来自动定时运行脚本
    optional: use crontab to auto run the script:
#### &emsp;     i.在 bash gym.sh -i 查看提示 

#### &emsp;     ii.编辑crontab文件，输入定时命令
    crontab -e
#### &emsp;     iii.以早上10:55，每周一、二、三、四、日为例，crontab命令格式如下
    55 10 * * sun,mon,tue,wed,thu /bin/bash {absolute_path}/gym.sh # formation like this
#### &emsp;     iv.加载crond服务，使crontab设置生效
    service crond reload
    service crond restart
