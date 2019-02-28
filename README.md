# RemoteCheck

## 使用说明
输入:
```python
from remotecheck import map_with_multi_thread_output_json

host_list = [
    [
        '192.168.1.1',
        '22',
        'root',
        'admin123'
    ],
    [
        '192.168.1.2',
        '10022',
        'weblogic',
        'admin123'
    ]
]

result = map_with_multi_thread_output_json(host_list)

```
输出：
```json
{
    "0": {
        "hostname": "192.168.1.1",
        "ping_status": "NG",
        "port_status": "CLOSE[22]-timed out",
        "ssh_status": "-",
        "username": "root",
        "password": "admin123",
        "password_level": "WeakPassword",
        "reason": "密码复杂度不符合标准"
    },
    "1": {
        "hostname": "192.168.1.2",
        "ping_status": "NG",
        "port_status": "CLOSE[10022]-timed out",
        "ssh_status": "-",
        "username": "weblogic",
        "password": "admin123",
        "password_level": "WeakPassword",
        "reason": "密码复杂度不符合标准"
    }
}
```

## 模块说明
* check.py
* untils.py
* client.py

## 运行环境
* [python 3.7.1](https://www.python.org/downloads/)
* [paramiko](https://pypi.org/project/paramiko/)
* [ping3](https://pypi.org/project/ping3/)
* [python-levenshtein](https://download.lfd.uci.edu/pythonlibs/u2hcgva4/python_Levenshtein-0.12.0-cp37-cp37m-win_amd64.whl)
* [xlrd](https://pypi.org/project/xlrd/)
* [xlsxwriter](https://pypi.org/project/XlsxWriter/)

## 更新日志

**版本1.0 [2018/09/05]**

1. 实现了批量探测主机的连通性以及SSH的连通性
2. 添加ascii风格的表格输出,输出更美观
3. 添加动态进度条
4. 添加了读取excle表格的功能
5. 增加了Linux系统的支持

**版本2.0 [2018/09/18]**

1. 添加了excle输出的功能
2. 利用多线程加速探测速度,最高每秒1000个并发
3. 增加了配置文件,可对输入输出的文件名称进行指定
4. 优化了ping探测效率,一旦ping通将直接跳过第二次ping
5. 使用推导表达式优化了读取excle的效率
6. 优化了ssh探测的稳定性,基本不会出现No existing session这类检查失败的结果了
7. 增加了ssh连接过程的debug输出,方便开发调试
8. 增加了port探测失败原因的输出

**版本3.0 [2018/09/19]**

1. 新增了密码复杂度检查功能,能够对密码长度,大小写,特殊符号要求进行检查.并计算密码与用户名的相识度.
2. 在输出结果中附带了账号和密码,方便用户比对结果.

**版本4.0 [2019/02/28]**
1. 将程序的每个功能都解耦,能够很好的对外提供服务.