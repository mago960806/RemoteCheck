import re
import socket

import paramiko
import Levenshtein
from ping3 import ping


class Check(object):
    def __init__(self):
        pass

    @staticmethod
    def ping_check(target_host):
        result = 'NG'
        for i in range(2):
            ping_delay = ping(target_host, timeout=0.5, unit='ms')
            # 一旦拿到结果立即退出循环避免重复执行
            if ping_delay is not None:
                result = 'OK[{}ms]'.format(round(ping_delay, 1))
                break
        return result

    @staticmethod
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

    @staticmethod
    def ssh_check(target_host, target_port, username, password):
        # paramiko.util.log_to_file('ssh_login.log')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=target_host, port=int(target_port), username=username, password=password, allow_agent=False, look_for_keys=False, timeout=5)
            result = 'Succeed'
            try:
                ssh.open_sftp()
            except paramiko.sftp.SFTPError as e:
                result = 'Failed:{}'.format(e)
        except Exception as e:
            result = 'Failed:{}'.format(e)
        finally:
            ssh.close()
        return result

    @staticmethod
    def passwd_check(username, password, password_length_require=8, password_similarity_require=0.8):
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

    def check(self, host_info):
        title_list = ['hostname', 'ping_status', 'port_status', 'ssh_status', 'username', 'password', 'password_level', 'reason']
        host, port, username, password = host_info
        port = int(port)
        ping_status = self.ping_check(host)
        port_status = self.port_check(host, port)
        passwd_status = self.passwd_check(username, password)

        if port_status.startswith('OPEN'):
            ssh_status = self.ssh_check(host, port, username, password)
            result = [host, ping_status, port_status, ssh_status] + [username, password] + passwd_status
        else:
            result = [host, ping_status, port_status, '-'] + [username, password] + passwd_status
        result = dict(zip(title_list, result))
        return result


if __name__ == '__main__':
    check = Check().check(['127.0.0.1', '80', 'root', 'admin123'])
    print(check)
