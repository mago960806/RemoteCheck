import os
import re
import socket
import platform
from configparser import RawConfigParser
from concurrent.futures import ThreadPoolExecutor

import xlrd
import xlsxwriter
import paramiko
from ping3 import ping
from tqdm import tqdm
import Levenshtein


# 日志相关配置
config = RawConfigParser()
if os.path.exists('RemoteCheck.conf'):
    config.read('RemoteCheck.conf')
else:
    # 不存在配置文件则创建
    config.add_section('Common')
    config.set('Common', 'input_filename', 'host_list.xlsx')
    config.set('Common', 'output_filename', 'result.xlsx')
    config.add_section('PasswordCheck')
    config.set('PasswordCheck', 'password_length_require', '8')
    config.set('PasswordCheck', 'password_similarity_require', '0.8')
    config.add_section('Thread')
    config.set('Thread', 'thread_num', '100')
    # 创建完毕后再次读取配置文件
    with open('RemoteCheck.conf', 'w') as config_file:
        config.write(config_file)
    config.read('RemoteCheck.conf')

input_filename = config.get('Common', 'input_filename')
output_filename = config.get('Common', 'output_filename')

password_length_require = config.getint('PasswordCheck', 'password_length_require')
password_similarity_require = config.getfloat('PasswordCheck', 'password_similarity_require')

thread_num = config.getint('Thread', 'thread_num')


def read_excle():

    workbook = xlrd.open_workbook(input_filename)
    sheet = workbook.sheet_by_index(0)
    # 获取表格总行数
    nrows = sheet.nrows
    # 使用列表的推导表达式批量取出每行的数据(除去表格标题)
    host_list_excle = [sheet.row_values(i) for i in range(1, nrows)]
    return host_list_excle


def read_file():

    with open('host_list.txt') as file:
        # 使用列表的推导表达式逐行读取文本并对每行的内容进行split操作
        host_list_text = [rows.split(' ')for rows in file.readlines()]
    return host_list_text


def ping_check(target_host):

    result = 'NG'
    for i in range(2):
        ping_delay = ping(target_host, timeout=0.5, unit='ms')
        # 一旦拿到结果立即退出循环避免重复执行
        if ping_delay is not None:
            result = 'OK[{}ms]'.format(round(ping_delay, 1))
            break
    return result


def port_check(target_host, target_port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((target_host, int(target_port)))
        result = 'OPEN[{}]'.format(target_port)
    # except ConnectionRefusedError:
    #     result = 'CLOSE[{}]'.format(target_port)
    # except socket.timeout:
    #     result = 'CLOSE[{}]'.format(target_port)
    except Exception as e:
        result = 'CLOSE[{}]-{}'.format(target_port, e)
    s.close()
    return result


def ssh_check(target_host, target_port, username, password):

    paramiko.util.log_to_file('ssh_login.log')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=target_host, port=int(target_port), username=username, password=password,
                    allow_agent=False, look_for_keys=False, timeout=5)
        result = 'Succeed'
    except Exception as e:
        result = 'Failed:{}'.format(e)
    finally:
        ssh.close()
    return result


def passwd_check(username, password):

    pattern = re.compile(
        r'[-\da-zA-Z`=\\;,./~!@#$%^&*()_+|{}:<>?]*((\d+[a-zA-Z]+'
        r'[-`=\\;,./~!@#$%^&*()_+|{}:<>?]+)|(\d+[-`=\\;,./~!@#$%^&*()_+|{}:<>?]+'
        r'[a-zA-Z]+)|([a-zA-Z]+\d+[-`=\\;,./~!@#$%^&*()_+|{}:<>?]+)|([a-zA-Z]+'
        r'[-`=\\;,./~!@#$%^&*()_+|{}:<>?]+\d+)|([-`=\\;,./~!@#$%^&*()_+|{}:<>?]+'
        r'\d+[a-zA-Z]+)|([-`=\\;,./~!@#$%^&*()_+|{}:<>?]+'
        r'[a-zA-Z]+\d+))[-\da-zA-Z`=\\;,./~!@#$%^&*()_+|{}:<>?]*')
    ratio = Levenshtein.ratio(username, password)

    length_enough = True if len(password) >= password_length_require else False
    vaild_password = re.match(pattern, password)
    similar_password = True if ratio > password_similarity_require else False

    if length_enough:
        if vaild_password:
            if not similar_password:
                result = ['StrongPassword', '密码复杂性符合标准']
            else:
                result = ['WeakPassword', '密码与用户名相似度太高']
        else:
            result = ['WeakPassword', '密码复杂度不符合标准']
    else:
        result = ['WeakPassword', '密码长度小于8位']

    return result
# def output_table(host_lists):
#     index = 1
#     for host_info in tqdm(host_lists, desc='Checking', ascii=True):
#         host, port, username, password = host_info
#         port = int(port)
#         ping_status = ping_check(host)
#         port_status = port_check(host, port)
#         if port_status.startswith('OPEN'):
#             ssh_status = ssh_check(host, port, username, password)
#             table.add_row([index, host, ping_status, port_status, ssh_status])
#         else:
#             table.add_row([index, host, ping_status, port_status, '-'])
#         index += 1
#     print(table)


# def check(host_info):
#     global index
#     host, port, username, password = host_info
#     port = int(port)
#     ping_status = ping_check(host)
#     port_status = port_check(host, port)
#     if port_status.startswith('OPEN'):
#         ssh_status = ssh_check(host, port, username, password)
#         result = [index, host, ping_status, port_status, ssh_status]
#     else:
#         result = [index, host, ping_status, port_status, '-']
#     index += 1
#     return result


def check(host_info):

    host, port, username, password = host_info
    port = int(port)
    ping_status = ping_check(host)
    port_status = port_check(host, port)
    passwd_status = passwd_check(username, password)

    if port_status.startswith('OPEN'):
        ssh_status = ssh_check(host, port, username, password)
        result = [host, ping_status, port_status, ssh_status] + [username, password] + passwd_status
    else:
        result = [host, ping_status, port_status, '-'] + [username, password] + passwd_status
    return result


def one_thread_run(host_lists):
    # 06:36
    for host_info in tqdm(host_lists, desc='Checking', ascii=True):
        check(host_info)


# def multi_thread_output_excle(host_lists):
#     # 创建线程池
#     thread_pool = []
#     # 创建Excle表格
#     workbook = xlsxwriter.Workbook('result.xlsx')
#     worksheet = workbook.add_worksheet('端口基线表')
#     # 自动填充标题
#     title_col = 0
#     for title in table.field_names:
#         worksheet.write(0, title_col, title)
#         title_col += 1
#     # 开始多线程跑任务
#     for host_info in host_lists:
#         t = TaskThread(check, args=(host_info,))
#         thread_pool.append(t)
#         t.start()
#     for t in tqdm(thread_pool, desc='Checking', ascii=True):
#         t.join()
#         rows = t.get_result()
#         context_col = 0
#         for row in rows:
#             worksheet.write(index, context_col, row)
#             context_col += 1
#     workbook.close()
#     print('输出文件保存在：{}'.format(os.getcwd()+os.path.sep+'result.xlsx'))


def map_with_multi_thread_output_excle(host_lists):
    # 创建Excle表格
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet('端口基线表')
    # 自动填充标题
    title_col = 0
    # 索引初始值
    index = 1
    title_list = ['Index', 'Host', 'PingCheck', 'PortCheck', 'SSH',
                  'UserName', 'Password', 'PasswordCheck', 'PasswordCheckReason']
    for title in title_list:
        worksheet.write(0, title_col, title)
        title_col += 1
    # 创建线程池
    thread_pool = ThreadPoolExecutor(max_workers=thread_num)
    tasks = thread_pool.map(check, host_lists)
    for result in tqdm(tasks, desc='Checking', ascii=True, total=len(host_lists)):
        context_col = 0
        # 插入Index数据
        result.insert(0, index)
        # 将结果取出来并向单元格中写入数据
        for row in result:
            worksheet.write(index, context_col, row)
            context_col += 1
        index += 1
    workbook.close()
    print('输出文件保存在：{}'.format(os.getcwd() + os.path.sep + 'result.xlsx'))


# def as_completed_with_multi_thread_output_excle(host_lists):
#     # 创建线程池
#     thread_pool = ThreadPoolExecutor(max_workers=500)
#     # 创建Excle表格
#     workbook = xlsxwriter.Workbook('result.xlsx')
#     worksheet = workbook.add_worksheet('端口基线表')
#     # 自动填充标题
#     title_col = 0
#     for title in table_field_names:
#         worksheet.write(0, title_col, title)
#         title_col += 1
#     # 使用链表推导式将线程对象压入线程池中
#     thread_pool = [thread_pool.submit(check, host_info) for host_info in host_lists]
#     for future in tqdm(as_completed(thread_pool), desc='Checking', ascii=True):
#         rows = future.result()
#         print(rows)
#         context_col = 0
#         for row in rows:
#             worksheet.write(index, context_col, row)
#             context_col += 1
#     workbook.close()
#     print('输出文件保存在：{}'.format(os.getcwd() + os.path.sep + 'result.xlsx'))


if __name__ == '__main__':
    # 不同操作系统读取的文件不同
    if platform.system() == 'Windows':
        host_list = read_excle()
    else:
        try:
            host_list = read_file()
        except FileNotFoundError:
            print('请创建host_list.txt文件并写入需要核查的数据')
            exit(1)
    # 开启多线程执行check函数
    map_with_multi_thread_output_excle(host_list)
    input('Press <Enter> exit...')
