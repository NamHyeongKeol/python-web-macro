import sqlite3
import time


from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException


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

    elif user.page.name == 'bbasak':
        id_form = driver.find_element_by_id('login_id')
        pw_form = driver.find_element_by_id('login_pw')
        id_form.send_keys(user.id)
        pw_form.send_keys(user.pw)
        btn_login = driver.find_element_by_class_name('btn_login')
        btn_login.click()

    elif user.page.name == 'phoneview':
        id_form = driver.find_element_by_id('mb_id')
        pw_form = driver.find_element_by_id('mb_password')
        id_form.send_keys(user.id)
        pw_form.send_keys(user.pw)
        btn_login = driver.find_element_by_class_name('btn-block')
        btn_login.click()

    else:
        return


def logout(driver, user):
    if user.page.name == 'hogaeng':
        driver.get('https://hogaeng.co.kr/g4s/bbs/logout_pc_ssl.php')

    elif user.page.name == 'bbasak':
        driver.get('http://bbasak.com/bbs/logout.php')

    elif user.page.name == 'phoneview':
        driver.get('http://myphoneview.com/bbs/logout.php')

    else:
        return


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

    elif user.page.name == 'bbasak':
        driver.get(user.page.url + '/bbs/write.php?bo_table=com25')
        title = driver.find_element_by_name('wr_subject')
        title.send_keys('출석')
        time.sleep(1)
        iframe = driver.find_element_by_tag_name('iframe')
        driver.switch_to_frame(iframe)
        content = driver.find_element_by_class_name('cke_contents_ltr')
        content.send_keys('출석')
        driver.switch_to_window('')
        chains = ActionChains(driver)
        submit_btn = driver.find_element_by_id('submit_img')
        chains.move_to_element(submit_btn).click().perform()

    elif user.page.name == 'phoneview':
        driver.get(user.page.url + '/bbs/board.php?bo_table=attendance')
        chulsuk_book = driver.find_element_by_id('talk_submit')
        chulsuk_book.click()
        try:
            message = Alert(driver).text
        except NoAlertPresentException as e:
            print('asdf')
            return True

        if message == '이미 출석하셨습니다.':
            Alert(driver).accept()

            return False

        elif '축하합니다!' in message:
            Alert(driver).accept()

            return True

        else:
            raise Exception

    else:
        return


def get_point(driver, user):
    driver.get(user.page.url)
    if user.page.name == 'hogaeng':
        elem = driver.find_element_by_class_name('ol_point_area')
        textl = elem.find_element_by_class_name('textl')
        point_tag = textl.find_element_by_class_name('ocolor')

        return point_tag.text

    elif user.page.name == 'bbasak':
        elem = driver.find_element_by_id('gm')
        lis = elem.find_elements_by_tag_name('li')

        return lis[3].text.split('\n')[1].split('/')[0]

    elif user.page.name == 'phoneview':
        elem = driver.find_element_by_class_name('red')

        return elem.text

    else:
        return


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
        if user.page.url == driver.current_url:
            pass
        else:
            access(driver, user)
        login(driver, user)
        prepoint = get_point(driver, user)
        flag = attendance_check(driver, user)
        postpoint = get_point(driver, user)
        print('{}: {}\'s point: {} -> {}'.format(user.page.name, user.id, prepoint, postpoint))
        time.sleep(1)
        logout(driver, user) 

main()
