# coding=utf-8
from Logic.log_print import LogPrint
from Logic.interface_deal import InterfaceDeal
import json
import hashlib
import os
import xlrd                                                                                                             # 操作xlsx文件的库
import base64                                                                                                           # 生成的编码可逆,速度快,生成ascii字符,但是容易破解,仅适用于加密非关键信息的场合
from pyDes import *                                                                                                     # 使用pydes库进行des加密


class ExcelDeal:
    # 获取执行测试用例
    def runtest(self,testcase):
        # join()函数是连接字符串数组,os.path.join()函数是将多个路径组合后返回,os.getcwd()是返回当前进程的工作目录,testcase是测试用例文件的目录地址
        testcase = os.path.join(os.getcwd(),testcase)
        if not os.path.exists(testcase):
            lp = LogPrint()
            lp.error('测试用例文件不存在！')
            sys.exit()
        test_case = xlrd.open_workbook(testcase)  # 打开文件
        table = test_case.sheet_by_index(0)  # 根据shell索引获取sheet内容
        pwd = '123456'
        error_case = []  # 用于保存接口返回的内容和HTTP状态码

        for i in range(1, table.nrows):  # 循环行列表数据,table.nrows是获取行数
            # table.cell().value获取某个单元格的内容值,该方法第一个参数是行数,第二个参数是列数
            if table.cell(i, 9).value.replace('\n', '').replace('\r','') != 'Yes':
                continue
            num = str(int(table.cell(i, 0).value)).replace('\n', '').replace('\r', '')
            api_purpose = table.cell(i, 1).value.replace('\n', '').replace('\r', '')
            api_host = table.cell(i, 2).value.replace('\n', '').replace('\r', '')
            request_url = table.cell(i, 3).value.replace('\n', '').replace('\r', '')
            request_method = table.cell(i, 4).value.replace('\n', '').replace('\r', '')
            request_data_type = table.cell(i, 5).value.replace('\n', '').replace('\r', '')
            request_data = table.cell(i, 6).value.replace('\n', '').replace('\r', '')
            encryption = table.cell(i, 7).value.replace('\n', '').replace('\r', '')
            check_point = table.cell(i, 8).value.replace('\n', '').replace('\r', '')
            # correlation = table.cell(i,9).value.replace('\n','').replace('\r','').split(';')

            ifd = InterfaceDeal()
            status = resp = ''
            if encryption == 'MD5':  # 如果数据采用md5加密，便先将数据加密,这里加密的密码需要跟不同接口的session有关系
                request_data = json.loads(request_data)
                request_data['pwd'] = hashlib.md5().update(request_data['pwd']).hexdigest()
                status, resp = ifd.interface_test(num, api_purpose, api_host, request_url, request_method,
                                                  request_data_type, request_data, check_point)
            elif encryption == 'DES':  # 数据采用des加密
                k = des('secretKEY', padmode=PAD_PKCS5)
                des_password = base64.b64encode(k.encrypt(json.dumps(pwd)))
                status, resp = ifd.interface_test(num, api_purpose, api_host, request_url, request_method,
                                                  request_data_type, des_password, check_point)

            if status != 200:  # 如果状态码不为200,那么证明接口产生错误,保存错误信息。
                error_case.append((num + '、' + api_purpose, str(status) + api_host + request_url, resp))
                continue
        return error_case
