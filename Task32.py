import selenium
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import re
import pymongo

browser = selenium.webdriver.Chrome()
wait = WebDriverWait(browser, 10)
MONGO_URL = 'localhost'
MONGO_DB = 'Task33'
MONGO_TABBLE11 = 'content1'
MONGO_TABBLE22 = 'content2'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

#471页开始
def open():
    try:
        browser.get('http://jzzb.cqjsxx.com/CQ_ZB/ForeDisplay/ZBAffiche_Info/ZBAffiche_Info.aspx')
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#Pager1_Pages')))
        return total.text
    except TimeoutException:
        return open()


def save_to_mongo1(result):
    try:
        db[MONGO_TABBLE11].insert(result)
        print(result, "存储到mongodb成功")
    except Exception:
        print(result, "存储到mongodb不成功")

def save_to_mongo2(result):
    try:
        db[MONGO_TABBLE22].insert(result)
        print(result, "存储到mongodb成功")
    except Exception:
        print(result, "存储到mongodb不成功")

def find():
    html = browser.page_source
    html = etree.HTML(html)
    find_urls2 = html.xpath('//*[@id="DataGrid1"]/tbody/tr/td/font/a//text()')
    find_urls = browser.find_elements_by_xpath('//*[@id="DataGrid1"]/tbody/tr/td/font/a')
    # print(find_urls)
    find_titles = html.xpath('//*[@id="DataGrid1"]/tbody/tr/td/font/a/font//text()')
    # print(len(find_titles))
    # time选项包含了公示日期
    find_times = html.xpath('//*[@id="DataGrid1"]/tbody/tr/td[4]/font//text()')
    del find_times[0]
    # print(len(find_times))
    # companies包含了中标单位
    find_companies = html.xpath('//*[@id="DataGrid1"]/tbody/tr/td[3]/font//text()')
    del find_companies[0]
    # print(len(find_companies))
    answers = []
    answers.extend(find_titles)
    for i in range(0, len(answers)):
        #answers[i] = 'name: ' + find_titles[i] + "company: " + find_companies[i] + "time: " + find_times[i] + "url: " + find_urls2[i] + "\n"
        answers = {
            'name':find_titles[i],
            'company':find_companies[i],
            'time':find_times[i],
            'url':find_urls2[i],
        }
        save_to_mongo1(answers)
    #print(answers)


def next_page():
    next_page = wait.until(EC.element_to_be_clickable((By.ID, 'Pager1_LB_Next')))
    next_page.click()


def page_in():
    # 目前思路：先把’首页‘（即含有当前页面所有连接的页面获得句柄），然后点开这一页所有的链接，获得所有新窗口的句柄，利用句柄进行依次页面处理
    # 关闭新页面，回到最初页面，然后翻页https://www.cnblogs.com/tobecrazy/p/4117506.html
    current_windows = browser.current_window_handle
    for i in range(0, 15):
        # current_windows = browser.current_window_handle
        find_urls = browser.find_elements_by_xpath('//*[@id="DataGrid1"]/tbody/tr/td/font/a')
        url = find_urls[i]
        url.click()
    all_handles = browser.window_handles
    # 进入新打开链接窗口 
    for handle in all_handles:
        if handle != current_windows:
            browser.switch_to.window(handle)
            print(u"切换句柄成功")
            page_information()
            browser.close()
    # print (current_windows)   #输出主窗口句柄
    browser.switch_to.window(current_windows)  # 返回主窗口
    print("返回成功")


def page_information():
    print("yes")
    # print(browser.page_source)
    contents = browser.page_source
    contents = etree.HTML(contents)
    result = {}
    for i in range(1, 20):
        content = contents.xpath('//*[@id="Table3"]/tbody/tr[' + str(i) + ']//text()')
        # print(content)
        if (content == []):
            break
        while "\r\n" in content:
            content.remove("\r\n")
        while "/" in content:
            content.remove("/")
        content = [''.join(x.split()) for x in content]
        # 这是列表内每个元素去除xa0等空白字符
        content = ''.join(content)
        # print(content)
        project = u'(工程名称.*)'
        project_num = u'(招标编码.*)'
        zb_person = u'(招标人.*)'
        fh_p = u'(中标单位:第一.*)第二'
        sh_p = u'(第二：.*)第三'
        th_p = u'(第三：.*)'
        manager = u'(项目经理.*)'
        money = u'(中标价.*)中标工期'
        gov = u'(审批部门.*)'
        per = u'(核准人.*)'

        pro_name = re.findall(project, content, re.S)
        if pro_name != []:
            result.update({'project':pro_name[0]})
            # print(pro_name)

        pro_num = re.findall(project_num, content, re.S)
        if pro_num != []:
            result.update({'project_num':pro_num[0]})
            # print(pro_num)

        zb_p = re.findall(zb_person, content, re.S)
        if zb_p != []:
            result.update({'zhaobiao_p':zb_p[0]})
            # print(zb_p)

        fh_pn = re.findall(fh_p, content, re.S)
        if fh_pn != []:
            result.update({'first':fh_pn[0]})
            # print(fh_pn)

        sh_pn = re.findall(sh_p, content, re.S)
        if sh_pn != []:
            result.update({'second':sh_pn[0]})
            # print(sh_pn)

        th_pn = re.findall(th_p, content, re.S)
        if th_pn != []:
            result.update({'third':th_pn[0]})
            # print(th_pn)

        man = re.findall(manager, content, re.S)
        if man != []:
            result.update({'man':man[0]})
            # print(man)

        mon = re.findall(money, content, re.S)
        if mon != []:
            result.update({'money':mon[0]})
            # print(mon)

        gov_n = re.findall(gov, content, re.S)
        if gov_n != []:
            result.update({'government':gov_n[0]})
            # print(gov_n)

        per_n = re.findall(per, content, re.S)
        if per_n != []:
            result.update({'person':per_n[0]})
            # print(per_n)
    #print(result)
    save_to_mongo2(result)

def main():
    total = int(open())
    print(total)
    for j in range(0,472):
        next_page()
    if j ==471:
        for i in range(470,601):
            print("page:", i + 1)
            find()
            page_in()
            if i+1==total:
                break
            else:
                next_page()


if __name__ == '__main__':
    main()
