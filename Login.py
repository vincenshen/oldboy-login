# -*- coding:utf-8 -*-
import sqlite3,os,hashlib,time
import getpass      # pycharm不支持getpass包，请不要在pycharm中执行该程序

# 创建表
def create(conn):
    conn.execute('''CREATE TABLE USER
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            lock TEXT NOT NULL DEFAULT 'False',
            locktime FLOAT DEFAULT NULL )''')
    conn.commit()

# 通过用户名查询密码/锁定状态/锁定时间
def select(conn,user_name):
    passwd = conn.execute("SELECT password, lock, locktime from USER WHERE username = ?",(user_name,))
    return passwd.fetchone()

# 创建用户
def insert(conn,name,passwd):
    try:
        conn.execute("INSERT INTO USER (username,password) VALUES ('%s','%s')" % (name, passwd))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print('User ID already exists, Please use a different!')

# 更新用户锁定状态/锁定时间
def update(conn,user_name,lock,locktime):
    conn.execute("UPDATE USER set lock = '%s',locktime = '%s' where username='%s'" % (lock,locktime,user_name))
    conn.commit()

if __name__ == '__main__':

    #断users.db是否已存在
    if not os.path.exists('users.db'):
        conn = sqlite3.connect('users.db')
        create(conn)
        user_name = 'alex'
        user_passwd = b'tesla'
        # 创建用户,密码使用md5加密后存入数据库
        insert(conn, user_name, hashlib.md5(user_passwd).hexdigest())
        print("Init a test user (%s) and password (%s)!"%(user_name, user_passwd))
    else:
        conn = sqlite3.connect('users.db')
    # 定义三次登录机会
    login_false_count = 3
    while login_false_count > 0:
        user_name = input('Please Enter Username:').strip()
        if len(user_name) == 0:
            continue
        # 调用getpass使输入的密码不直接打印在屏幕
        user_passwd = bytes(getpass.getpass(),encoding='utf8')
        try:
            user_info = select(conn, user_name)     # 通过用户名查询用户密码/锁定状态/锁定时间
            if user_info[1] == 'True':      # 判断用户是否已锁定
                if (time.time() - user_info[2]) > 1800:     # 判断锁定是否超过30分钟
                    update(conn, user_name, 'False', None)      # 超过30分钟设置用户锁定字段为False,并清除锁定时间
                    if user_info[0] == hashlib.md5(user_passwd).hexdigest():    # 判断密码是否正确
                        print('Welcome %s' % user_name)
                        break
                    else:
                        login_false_count -= 1
                        print('Username or Password error! Your can login %d times!' % login_false_count)
                else:
                    print('Login Failed! Your account have been locked, it will be unlocked after %s minutes, please try again later!'%int((1800-(time.time() - user_info[2]))/60))
                    break
            else:
                if user_info[0] == hashlib.md5(user_passwd).hexdigest():    # 判断密码是否正确
                    print('Login Success, Welcome %s!' % user_name)
                    break
                else:
                    login_false_count -= 1
                    print('Username or Password error! Your can login %d times!' % login_false_count)
        except TypeError as e:
            print('User ID does not exist!')
            continue
        if login_false_count == 0:
            update(conn, user_name, 'True', time.time())     # 密码尝试3次后，调用update函数将用户的locked字段设置为True
            print('Your account is locked and automatic unlocking after 30 minutes, please try again later!')
    conn.close()