import selenium.webdriver.firefox.service
import selenium.webdriver.firefox.options
import selenium.webdriver.firefox.firefox_profile
import os
import time
import pathlib
import configparser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
import http.client
import webbrowser
import requests
import datetime

def normal_input(content):
    now = datetime.datetime.now()
    s=input("[{}:{}:{} {}:{}:{}.{}]   {}".format(now.year,now.month,now.day,now.hour,now.minute,now.second,str(now.microsecond)[:2],content))
    return s

def normal_print(content:str):
    now=datetime.datetime.now()
    print("[{}:{}:{} {}:{}:{}.{}]   {}".format(now.year,now.month,now.day,now.hour,now.minute,now.second,str(now.microsecond)[:2],content))
    pass

def check_load_config():
    #文件配置
    # print(os.path.exists(r".\Profile"))
    if os.path.exists(r".\Profile"):
        pass
    else:
        os.makedirs(r".\Profile")
    if os.path.exists(r".\config.ini"):
        pass
    else:
        with open("config.ini","w",encoding="utf-8") as f:
            pass

    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

def BTBUaccount_setup():
    global config
    account=normal_input("请输入你的btbu账号")
    password=normal_input("请输入你等btbu密码")
    normal_print("你的账号:"+account)
    normal_print("你的密码:"+ password)
    confirmation=normal_input("是否确认？（Y,y/N,n）")
    while confirmation not in "YyNn":
        confirmation = normal_input("是否确认？（Y,y/N,n）")
    if confirmation in ["Y","y"]:
        config.set("accounts","BTBUaccount",account)
        config.set("accounts", "BTBUpassword", password)
        with open("config.ini","w",encoding="utf-8") as f:
            config.write(f)
    else:
        BTBUaccount_setup()


def account_setup():
    global config
    account=normal_input("请输入你的账号")
    password=normal_input("请输入你的密码")
    normal_print("你的账号:"+account)
    normal_print("你的密码:"+ password)
    confirmation=normal_input("是否确认？（Y,y/N,n）")
    while confirmation not in "YyNn":
        confirmation = normal_input("是否确认？（Y,y/N,n）")
    if confirmation in ["Y","y"]:
        config.set("accounts","account",account)
        config.set("accounts", "password", password)
        with open("config.ini","w",encoding="utf-8") as f:
            config.write(f)
    else:
        account_setup()

def account_verification():
    global config
    normal_print("正在验证账号")
    response=requests.get("https://raw.githubusercontent.com/MUSA1956/BTBUlogger/main/account.txt",stream=True, allow_redirects=True)
    if response.status_code == 200:
        account_text=response.text
        dic={}
        # print(account_text.split())
        for i in account_text.split():
            dic[i.split(":")[0]]=i.split(":")[1]
        if config["accounts"]["account"] in dic:
            if config["accounts"]["password"] == dic[config["accounts"]["account"]]:
                normal_print("账号验证成功")
            else:
                normal_print("账号信息无效，请重新设置账号信息。")
                account_setup()
                account_verification()
        else:
            normal_print("账号信息无效，请重新设置账号信息。")
            account_setup()
            account_verification()
    #访问github
    pass

def check_accounts():
    global config
    if "accounts" in config:
        #logger账号
        if "account" in config["accounts"] and "password" in config["accounts"]:
            pass
        else:
            account_setup()
        #btbu账号
        if "BTBUaccount" in config["accounts"] and "BTBUpassword" in config["accounts"]:
            pass
        else:
            BTBUaccount_setup()
    else:
        config.add_section("accounts")
        account_setup()
        BTBUaccount_setup()

def selenium_setup():
    normal_print("初始化selenium")
    firefox_service = selenium.webdriver.FirefoxService(executable_path=r"geckodriver.exe",log_output="geckodriver.log",port=4444,service_args=['--marionette-port', '2828'])
    firefox_options = selenium.webdriver.FirefoxOptions()

    firefox_options.add_argument(r"-profile")
    firefox_options.add_argument(r".\Profile")
    # firefox_profile = selenium.webdriver.FirefoxProfile()
    Driver=selenium.webdriver.Firefox(options=firefox_options,service=firefox_service)
    return Driver


def site_account_setup():
    global config,Driver
    normal_print("依据BTBU账号配置网站账号中")
    site_dic={"bb":{"site":"https://bb.btbu.edu.cn/",
                    "account":config["accounts"]["BTBUaccount"],
                    "password":config["accounts"]["BTBUaccount"],
                    "instructions":(("find_element","css selector","#user_id"),
                                    ("send","account"),
                                    ("find_element","css selector","#password"),
                                    ("send","password"),
                                    # ("find_element","css selector","#login"),
                                    # ("submit")
                                    ("send","Keys.RETURN"))},
              "jwgl":{"site":"https://jwgl.btbu.edu.cn/",
                      "account":config["accounts"]["BTBUaccount"],
                      "password":config["accounts"]["BTBUpassword"]}}
    return site_dic

def open_site(site_name:str):
    global Driver
    normal_print("正在启动"+site_name)
    account = site_dic[site_name]["account"]
    password = site_dic[site_name]["password"]
    Driver.switch_to.new_window("tab")
    Driver.get(site_dic[site_name]["site"])
    for i in site_dic[site_name]["instructions"]:
        time.sleep(0.5)
        if i[0] == "find_element":
            element=Driver.find_element(i[1],i[2])
            # print(element)
        elif i[0] == "send":
            element.send_keys(eval(i[1]))
        elif i[0] == "click":
            element.click()
        elif i[0]=="submit":
            element.submit()




# command_dic={"open":open_site}

def command_input():
    global Driver,config,site_dic
    while True:
        commands=normal_input("send your command:").split()
        if commands:
            command=commands[0]
            if command == "open":
                open_site(commands[1])
            elif command == "help":
                help_inf=("open <site> #site:bb",
                          "help #get help",
                          "exit #end program")
                for i in help_inf:
                    normal_print(i)

            elif command == "exit":
                normal_print("退出中")
                Driver.quit()
                break





if __name__ == "__main__":
    config=check_load_config()#加载
    check_accounts()#检测配置文件中是否存在账户，没有进入account_setup()
    account_verification()#在线验证账户
    site_dic=site_account_setup()
    Driver = selenium_setup()
    command_input()


