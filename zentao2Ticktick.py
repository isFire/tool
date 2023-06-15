import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# 配置禅道登录信息
ZENTAO_URL = 'http://ip:port/zentao'
ZENTAO_ACCOUNT = 'your username'
ZENTAO_PASSWORD = 'your password'

# 配置发件人和收件人信息
FROM_EMAIL = 'your send email'
FROM_EMAIL_PASSWORD = 'your send email password'
TO_EMAIL = 'your ticktick receive email'
SMTP_SERVER = 'smtp server address'

# 登录禅道获取 cookies
session = requests.session()
login_data = {'account': ZENTAO_ACCOUNT, 'password': ZENTAO_PASSWORD}
login_url = f'{ZENTAO_URL}/user-login.html'
session.post(login_url, data=login_data)

# 获取禅道 bug 列表页面
bug_url = f'{ZENTAO_URL}/my-bug-assignedTo.html'
response = session.get(bug_url)

# 解析 bug 列表页面，获取新增的 bug
soup = BeautifulSoup(response.content, 'html.parser')
bug_table = soup.find('table', {'id': 'bugList'})
new_bugs = []
index = 1
for row in bug_table.find_all('tr')[1:]:
    bug_id = row.find_all('td')[0].text.strip()
    if bug_id is not None:
        title = row.find_all('a', {'href': '/zentao/bug-view-' + bug_id + '.html'})[0].text.strip()
        level = row.find_all('span', {'class': 'label-severity-custom'})[0].attrs['title']
        bug_url = f'{ZENTAO_URL}/bug-view-' + bug_id + '.html'
        product = ''
        response = session.get(bug_url)
        # 解析 bug 列表页面，获取新增的 bug
        bug_soup = BeautifulSoup(response.content, 'html.parser')
        bug_detail = bug_soup.find('div', {'id': 'legendBasicInfo'}).find("table")
        for detail in bug_detail.find_all('tr'):
            d = detail.find_all('th')[0]
            if d.text.strip() == '优先级':
                level = int(detail.find_all('td')[0].text.strip())
            if d.text.strip() == '所属产品':
                product = detail.find_all('td')[0].text.strip()

        desc = bug_soup.find('div', {'id': 'mainContent'}).find('div', {'class': 'main-col col-8'}).text.strip()
        bug = {
            'id': bug_id,
            'title': title,
            'level': level,
            'product': product,
            'desc': desc

        }
        new_bugs.append(bug)

mapping = {1: '高优先级', 2: '中优先级', 3: '低优先级', 4: '无优先级', 'xxx': 'xx项目',
           'xx2': 'xxx2项目'}

# 如果有新增 bug，则发送邮件
if len(new_bugs) > 0:
    # 发送邮件
    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as smtp:
        smtp.login(FROM_EMAIL, FROM_EMAIL_PASSWORD)
        for bug in new_bugs:
            # 生成邮件正文
            msg = MIMEText(str(bug), 'html')
            title = '[' + bug['title'] + ' #Bug型 #' + mapping.get(bug['product']) + \
                    ' ~list 今天 !' + mapping.get(bug['level']) + ' ](' + ZENTAO_URL + '/bug-view-' + bug[
                        'id'] + '.html'')'

            print(title)
            msg['Subject'] = title
            msg['From'] = FROM_EMAIL
            msg['To'] = TO_EMAIL
            smtp.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        print('Email sent.')
else:
    print('No new bugs found.')
