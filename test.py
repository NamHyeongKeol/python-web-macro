import sqlite3


from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.common.alert import Alert


Page = namedtuple('Page', ['name', 'url'])
User = namedtuple('User', ['id', 'pw', 'page'])


def init(driver=None):
    driver = webdriver.Chrome('./chromedriver')

    return driver


def access(driver, user):
    driver.get(user.page.url)


def login(driver, user):
    if user.page.name == 'hogaeng':
        login_area = driver.find_element_by_id('login_area')
        id_form = login_area.find_element_by_id('sir_ol_id')
        pw_form = login_area.find_element_by_id('sir_ol_pw')
        id_form.send_keys(user.id)
        pw_form.send_keys(user.pw)
        submit_form = login_area.find_element_by_id('sir_ol_submit')
        submit_form.click()


def logout(driver, user):
    if user.page.name == 'hogaeng':
        driver.get('https://hogaeng.co.kr/g4s/bbs/logout_pc_ssl.php')


def attendance_check(driver, user):
    if user.page.name == 'hogaeng':
        driver.get(user.page.url + '/attendance.php')
        att_btn = driver.find_element_by_id('att-btn')
        att_btn.click()
        message = Alert(driver).text

        if message == '출석체크는 하루에 한번만 가능합니다.':
            Alert(driver).accept()

            return False

        elif message == '출석체크완료':
            Alert(driver).accept()

            return True

        else:
            raise Exception


def get_point(driver, user):
    driver.get(user.page.url)
    if user.page.name == 'hogaeng':
        elem = driver.find_element_by_class_name('ol_point_area')
        textl = elem.find_element_by_class_name('textl')
        point_tag = textl.find_element_by_class_name('ocolor')

        return point_tag.text


def db_connect():
    return sqlite3.connect('db.sqlite3')


def get_page_list(conn):
    c = conn.cursor()

    c.execute('select * from Page')
    page_rows = c.fetchall()
    page_list = [Page(*page) for page in page_rows]

    return page_list


def get_user_list(conn):
    c = conn.cursor()

    c.execute('select id, pw, page_name, url from User join Page on User.page_name = Page.name')
    user_rows = c.fetchall()
    user_list = [User(*user[:2], Page(*user[-2:])) for user in user_rows]

    return user_list


def main():
    conn = db_connect()
    page_list = get_page_list(conn)
    user_list = get_user_list(conn)

    driver = init()

    for user in user_list:
        access(driver, user)
        login(driver, user)
        flag = attendance_check(driver, user)
        print('{}\'s point : '.format(user.id), get_point(driver, user))
        logout(driver, user) 

