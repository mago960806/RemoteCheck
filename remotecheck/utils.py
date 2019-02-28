import os
from uuid import uuid4

import xlrd
import xlsxwriter


def read_from_text(filepath, split_by=' '):
    with open(filepath) as file:
        result = [rows.split('{}'.format(split_by)) for rows in file.readlines()]
    return result


def read_from_excel(filepath, index=0):
    workbook = xlrd.open_workbook(filepath)
    sheet = workbook.sheet_by_index(index)
    result = [sheet.row_values(i) for i in range(1, sheet.nrows)]
    return result


def list_to_excel(list_object, filename=str(uuid4()) + '.xlsx'):
    with xlsxwriter.Workbook(filename) as workbook:
        worksheet = workbook.add_worksheet()
        row_num = 1
        for rows in list_object:
            col_num = 0
            # 插入索引号
            rows.insert(0, row_num)
            for row in rows:
                worksheet.write(row_num, col_num, str(row))
                col_num += 1
            row_num += 1
    print('[*] 输出文件保存在：{}'.format(os.getcwd() + os.path.sep + filename))


def dict_to_excel(dict_object, filename=str(uuid4()) + '.xlsx'):
    with xlsxwriter.Workbook(filename) as workbook:
        worksheet = workbook.add_worksheet()
        # 写入标题
        title_col = 0
        for key, value in dict_object[0].items():
            worksheet.write(0, title_col, key)
            title_col += 1
        # 写入数据
        row_num = 1
        for rows in dict_object:
            col_num = 0
            for key, value in rows.items():
                worksheet.write(row_num, col_num, str(value))
                col_num += 1
            row_num += 1
    print('[*] 输出文件保存在：{}'.format(os.getcwd() + os.path.sep + filename))


if __name__ == '__main__':
    a = [
        {
            'a': '123',
        },
        {
            'b': '456'
        }
    ]
    dict_to_excel(dict_object=a)
