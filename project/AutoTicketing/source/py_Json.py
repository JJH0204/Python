import json
import os

json_Dir = 'project/AutoTicketing/json/'

# 로그인 정보 json 파일 초기값
login_data = {
    'search_Site': 'https://www.interpark.com/',
    'login_type': 'local',
    'login_data': {
        'local': {
            'id': 'your_id',
            'password': 'your_pwd'
        },
        'kakao': {
            'id': 'your_id',
            'password': 'your_pwd'
        },
        'google': {
            'id': 'your_id',
            'password': 'your_pwd'
        },
        'naver': {
            'id': 'your_id',
            'password': 'your_pwd'
        }
    }
}

# 드라이브 초기 설정값
drive_setup = {
    "driver_path": "ChromeDrive_Path",
    "window_size": {
        "width": 1900,
        "length": 1000
    }
}

# 검색에 필요한 데이터 초기 설정값
search_data = {
    "search_Key": "Search key value",
    "number_of_seats_to_select": 1, # 필요한 자리 갯수
    "search_Type": "search_URL",    # 검색 키 검색 방법
    "search_Type_comment": "search_URL or search_field"
}

# json 파일 불러오기
def json_Read(Dir):
    with open(Dir+'.json', 'r') as json_file:
        config = json.load(json_file)
    return config

# json 파일 저장하기
def json_Write(file_Name, data):
    with open(file_Name+'.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    return

# json 파일 초기화
def json_Init(fileName):
    try:
        if os.path.exists(json_Dir + fileName):
            return json_Read( json_Dir + fileName)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        if fileName == 'login_data':
            json_Write( json_Dir + fileName,  login_data)
            return login_data
        elif fileName == 'drive_setup':
            json_Write( json_Dir + fileName,  drive_setup)
            return drive_setup
        elif fileName == 'search_data':
            json_Write( json_Dir + fileName,  search_data)
            return search_data

def json_Check(loginData, searchData):
    case_A = loginData['login_data']['local']['id'] == login_data['login_data']['local']['id']
    case_B = loginData['login_data']['kakao']['id'] == login_data['login_data']['kakao']['id']
    case_C = loginData['login_data']['google']['id'] == login_data['login_data']['google']['id']
    case_D = loginData['login_data']['naver']['id'] == login_data['login_data']['naver']['id']
    case_E = searchData['search_Key'] == search_data['search_Key']

    if case_A and case_B and case_C and case_D:
        print(json_Dir+"login_data.json 파일에 로그인에 필요한 정보(id/pwd)를 입력해주세요.\n");
        return True
    elif case_E:
        print(json_Dir+"search_data.json 파일에 검색어를 입력해주세요.\n");
        return True
    else:
        return False

def init_process():
    # json_Init(json_Dir+'\login_data', login_data)
    # json_Init(json_Dir+'\drive_setup', drive_setup)
    # json_Init(json_Dir+'\search_data', search_data)
    return

if __name__ == "__main__":
    init_process();