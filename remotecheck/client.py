import json
from concurrent.futures import ThreadPoolExecutor

from .check import Check
from .utils import read_from_excel, dict_to_excel


def map_with_multi_thread_output_excle(host_lists, max_workers=100):
    check = Check()
    # 创建线程池
    thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    tasks = thread_pool.map(check.check, host_lists)
    results = [task for task in tasks]
    dict_to_excel(results)
    return True


def run_test():
    host_list = read_from_excel('host_list.xlsx')
    map_with_multi_thread_output_excle(host_list)


def map_with_multi_thread_output_json(host_lists, max_workers=100):
    check = Check()
    # 创建线程池
    thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    tasks = thread_pool.map(check.check, host_lists)
    results = {key: value for key, value in enumerate(tasks)}
    return json.dumps(results)
