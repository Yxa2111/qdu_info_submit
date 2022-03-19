import requests, json, base64, hashlib
import jstyleson
import re
import os
import sys
from typing import *

FieldVal = NewType('FieldVal', Any)
FieldCode = NewType('FieldCode', str)
Field = Union[Tuple[FieldVal, FieldCode], FieldVal]
FieldKv = Tuple[str, Field]
templateItem = Tuple[str, str, str]

FieldContent: Dict[str, FieldVal] = {}

def get_value(d: Dict, keys: List):
    for key in keys:
        if key not in d:
            return None
        d = d[key]
    return d

class dataSet():
    def __init__(self, code_dict, init_value: Optional[Dict[str, Field]] = None) -> None:
        if init_value is None:
            init_value = {}
        self._init_vals: Dict[str, Field] = {}
        self._code_dict = code_dict
        for k, v in init_value.items():
            self.append(k, v)
    
    def get_geography_code(self, code_dict, loc_str):
        selected_code = None
        selected_str = ''
        loc_array = code_dict
        next = True
        while next:
            next = False
            for item in loc_array:
                if item['name'] in loc_str:
                    selected_code = item['code']
                    selected_str += item['name']
                    if item['children'] is not None:
                        loc_array = item['children']
                        next = True
                    break
        if selected_code is None:
            print('please check your location')
        else:
            print(f'select code {selected_code} location {selected_str}')
        return selected_code
    
    def append(self, key: str, value: Field):
        self._init_vals[key] = value
    
    def _find_val(self, key, type) -> Optional[FieldVal]:
        for k, v in self._init_vals.items():
            if key in k: # substr
                if type == 'area':
                    v = self.get_geography_code(self._code_dict, v)
                return v
        return None

    def fill(self, fields: List[Tuple[str, str, Optional[FieldCode]]], empty_value: Optional[str] = '') -> List[Field]:
        ret = []
        for key, type, code in fields:
            val = self._find_val(key, type)
            if val is None:
                if empty_value is None:
                    raise RuntimeError(f"we can't find value for key {key}, please update template.json")
                val = empty_value
            if code is None or isinstance(val, tuple):
                ret.append(val)
            else:
                ret.append((code, val))
        return ret

class signin:
    def __init__(self, usr: str, pwd: str):
        requests.packages.urllib3.disable_warnings()
        self.usr = usr  # 手机号
        self.pwd = pwd  # 密码
        # 定义一个session()的对象实体s来储存cookie
        self.s = requests.Session()
        # self.s.proxies = {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}
        # self.s.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; EBG-AN10 Build/HUAWEIEBG-AN10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36Ant-Android-WebView',
            'Authorization': 'BASIC '
                             'NTgyYWFhZTU5N2Q1YjE2ZTU4NjhlZjVmOmRiMzU3YmRiNmYzYTBjNzJkYzJkOWM5MjkzMmFkMDYyZWRkZWE5ZjY='
        }
        self.interUrl = 'https://h5api.xiaoyuanjijiehao.com/api/staff/interface'

    # 模拟登录
    def login(self):
        usr1 = "{\"LoginModel\":1,\"Service\":\"ANT\",\"UserName\":\"%s\"}" % self.usr
        log_url = "https://auth.xiaoyuanjijiehao.com/oauth2/token"
        data = {
            'password': hashlib.md5(self.pwd.encode()).hexdigest(),
            'grant_type': 'password',
            'username': str(base64.b64encode(usr1.encode('utf-8')), 'utf-8'),
        }
        req = self.s.post(log_url, headers=self.headers, data=data, verify=False)
        log_page = req.text
        # 获取请求头
        head = req.headers
        # 获取cookie
        cook = str(re.search("SERVERID=(.*?);Path=/", head.get("Set-Cookie")).group())
        cook = re.sub(";Path=/", "", cook)
        # print(cook)
        # 获取access_token
        token = json.loads(log_page.strip())["access_token"]
        # 更新header
        self.s.headers.update({'AccessToken': 'ACKEY_' + token})
        self.s.headers.update({'Cookie': cook})
        return self

def get_resp_data(resp, name):
    try:
        if resp['FeedbackCode'] == 0 and 'Data' in resp:
            return resp['Data']
        else:
            raise RuntimeError(name, " get response format error ", resp)
    except:
        raise RuntimeError(name, " get response format error ", resp)


class report:
    def __init__(self, usr: str, pwd: str):
        requests.packages.urllib3.disable_warnings()
        self.url = "https://h5api.xiaoyuanjijiehao.com/api/staff/interface"
        self.headers = {
            'Host': 'h5api.xiaoyuanjijiehao.com',
            'Connection': 'keep-alive',
            # 'Content-Length': '88',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; EBG-AN10 Build/HUAWEIEBG-AN10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36Ant-Android-WebView',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://h5api.xiaoyuanjijiehao.com',
            'X-Requested-With': 'com.zjelite.antlinkercampus',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://h5api.xiaoyuanjijiehao.com/h5/www1/11906/m_infocollect_formdesign/?x_ant_org=11906',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.si = signin(usr, pwd)
        self.si.login()
        # 获取报体温页面TaskCode

    def request(self, router, body):
        # 拼凑请求头
        thisHeader = self.headers
        # thisHeader.update({'Content-Length': '88'})
        thisHeader.update({'AccessToken': self.si.s.headers.get("AccessToken")})
        thisHeader.update(
            {'Cookie': str(self.si.s.headers.get("AccessToken")) + "; " + str(self.si.s.headers.get("Cookie"))})
        # 请求内容
        querystring = {
            "Router": router,
            "Method": 'POST',
            "Body": json.dumps(body)
        }
        return requests.post(self.url, headers=thisHeader, json=querystring, verify=False).json()

    def select_task(self, filter_keyword=None):
        # 拼凑请求头
        thisHeader = self.headers
        # thisHeader.update({'Content-Length': '88'})
        thisHeader.update({'AccessToken': self.si.s.headers.get("AccessToken")})
        thisHeader.update(
            {'Cookie': str(self.si.s.headers.get("AccessToken")) + "; " + str(self.si.s.headers.get("Cookie"))})
        # 请求内容
        querystring = {
            "Router": '/api/newcommtask/getstudenttasklist',
            "Method": 'POST',
            "Body": '{"UID":""}'
        }
        rep = requests.post(self.url, headers=thisHeader, json=querystring, verify=False).json()
        data = get_resp_data(rep, 'select_task')
        selected_item = data['list'][0]
        if filter_keyword:
            for item in data['list']:
                if filter_keyword in item['Title']:
                    selected_item = item
                    break
        print(f"select Title: {selected_item['Title']} TaskCode: {selected_item['TaskCode']} filter_keyword: {filter_keyword}")
        return selected_item['TaskCode'], selected_item['BusinessId']
    
    def get_dataset(self):
        data = get_resp_data(self.request('/api/system/getuserbaseinfo', {"UID":""}), 'get_baseinfo')
        global FieldContent
        fields = {
            '学院': (data['AcademyName'], 'disabled'),
            '年级': (data['UserCode'][0:4], 'disabled'),
            '专业': (data['MajorName'], 'disabled'),
            '班级': (data['ClassName'], 'disabled'),
            '学号': (data['UserCode'], 'disabled'),
            '姓名': (data['Name'], 'disabled')
        }
        fields = {**fields, **FieldContent}
        s = dataSet(self.get_geography(), fields)
        return s
    
    def get_fields(self, templateId) -> List[Tuple[str, str, Optional[FieldCode]]]:
        data = get_resp_data(self.request("/api/newcustomerform/get", {"TemplateId": templateId}), 'get_fields')
        content = json.loads(data['Content'])['list']
        ret = []
        for item in content:
            ret.append((item['name'], item['type'], None if 'fieldCode' not in item else item['fieldCode']))
        return ret
    
    def get_fields_template_item(self, templateId) -> List[templateItem]:
        data = get_resp_data(self.request("/api/newcustomerform/get", {"TemplateId": templateId}), 'get_fields')
        content = json.loads(data['Content'])['list']
        ret = []
        for item in content:
            if 'fieldCode' in item and item['fieldCode'] == 'disabled':
                continue
            comment = ''
            default_value = 'your value here'
            try:
                lst = get_value(item, ['options', 'options'])
                if lst is not None:
                    options = list(map(lambda i: i['value'], lst))
                    default_value = options[0]
                    comment = ', '.join(map(lambda s: f'"{s}"', options))
            except: pass
            ret.append((item['name'], default_value, comment))
        return ret
    
    def output_template_file(self, items: List[templateItem]):
        data = "{"
        for i in range(len(items)):
            name, value, comment = items[i]
            line = f'\n    "{name}": "{value}"'
            if i < len(items) - 1:
                line += ","
            line += f" // {comment}"
            data += line
        data += "\n}"
        with open('template.json', 'w', encoding='utf-8') as f:
            f.write(data)
    
    def generate_body_fields(self, fields: List[Field]):
        ret = []
        for field in fields:
            field_code = ''
            content = ''
            if isinstance(field, tuple):
                content, field_code = field
            else:
                content = field
            ret.append({
                "FieldCode": field_code,
                "Content": content
            })
        return ret
    
    def get_geography(self):
        return get_resp_data(self.request("/api/newcustomerform/geography", {}), 'get_geography')


def push_request(phone: str, password: str, filter_keyword=None):
    repo = report(phone, password)
    taskcode, templateId = repo.select_task(filter_keyword)
    s = repo.get_dataset()
    fields = repo.get_fields(templateId)
    fields = repo.generate_body_fields(s.fill(fields))
    print(f"fields: {fields}")
    body = {
        'Field': fields,
        "TaskCode": taskcode,
        "TemplateId": templateId,
    }
    resp = repo.request('/api/newcustomerform/submit', body)
    if resp["FeedbackCode"] == 0:
        return True
    return False

def main():
    options = {
        'phone': os.getenv('PHONE'),
        'password': os.getenv('PASSWORD'),
        'filter_keyword': os.getenv('KEYWORD')
    }
    print(options)
    if '-g' in sys.argv:
        repo = report(options['phone'], options['password'])
        repo.output_template_file(repo.get_fields_template_item(repo.select_task(options['filter_keyword'])[1]))
        print('update template.json')
        exit(0)
    load_template()
    result = push_request(**options)
    print(result)
    if not result:
        exit(-1)

def load_template():
    if os.path.exists('template.json') is False:
        print("template.json not found")
        return
    global FieldContent
    with open('template.json', encoding='utf-8') as f:
        FieldContent = jstyleson.loads(f.read())

if __name__ == '__main__':
    main()
