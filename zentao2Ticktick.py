import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# 配置禅道登录信息
ZENTAO_URL = 'zentao address,example: http://127.0.0.1/zentao'
ZENTAO_ACCOUNT = 'zentao username'
ZENTAO_PASSWORD = 'zentao password'

# 配置发件人和收件人信息
FROM_EMAIL = 'from email'
FROM_EMAIL_PASSWORD = 'email password'
TO_EMAIL = 'ticktick email'

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
        level = row.find_all('span', {'class': 'label-severity'})[0].attrs['title']
        bug = {
            'id': bug_id,
            'title': title,
            'level': level
        }
        new_bugs.append(bug)

# 如果有新增 bug，则发送邮件
if len(new_bugs) > 0:
    # 发送邮件
    with smtplib.SMTP_SSL('smtp.163.com', 465) as smtp:
        smtp.login(FROM_EMAIL, FROM_EMAIL_PASSWORD)
        for bug in new_bugs:
            # 生成邮件正文
            msg = MIMEText(str(bug), 'html')
            title = '[' + bug['title'] + ' #tag ~list ](' + ZENTAO_URL + '/zentao/bug-view-' + bug[
                'id'] + '.html'')'
            print(title)
            msg['Subject'] = title
            msg['From'] = FROM_EMAIL
            msg['To'] = TO_EMAIL
            smtp.send_message(msg)
        print('Email sent.')
else:
    print('No new bugs found.')


def getBugDetail(bug_id = bug_id) :
    bug_url = f'{ZENTAO_URL}/zentao/bug-view-' + bug_id + '.html'
    response = session.get(bug_url)
    # 解析 bug 列表页面，获取新增的 bug
    soup = BeautifulSoup(response.content, 'html.parser')
    bug_table = soup.find('table', {'id': 'bugList'})
