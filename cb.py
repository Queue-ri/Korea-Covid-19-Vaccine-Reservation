#!/usr/bin/env python3.9 -m nuitka
# -*- coding: utf-8 -*-
import browser_cookie3
import requests
import configparser
import json
import os
import sys
import time
from datetime import datetime
import telepot
import unicodedata
import urllib3
import re
import keyboard
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

urllib3.disable_warnings()

# DEPRECATED (~21.08.19)
# jar = browser_cookie3.chrome(domain_name=".kakao.com")
jar = {}

vaccine_candidates = [
    {"name": "아무거나", "code": "ANY"},
    {"name": "화이자", "code": "VEN00013"},
    {"name": "모더나", "code": "VEN00014"},
    {"name": "아스트라제네카", "code": "VEN00015"},
    {"name": "얀센", "code": "VEN00016"},
    {"name": "(예약불가)노바백스", "code": "VEN00017"},
    {"name": "(예약불가)시노팜", "code": "VEN00018"},
    {"name": "(예약불가)시노백", "code": "VEN00019"},
    {"name": "(예약불가)스푸트니크V", "code": "VEN00020"},
]


# 기존 입력 값 로딩
def load_config():
    config_parser = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        try:
            config_parser.read('config.ini')
            
            try:
                # 설정 파일이 있으면 최근 로그인 정보 로딩
                configuration = config_parser['config']
                previous_used_type = configuration["VAC"]
                previous_top_x = configuration["topX"]
                previous_top_y = configuration["topY"]
                previous_bottom_x = configuration["botX"]
                previous_bottom_y = configuration["botY"]
                previous_only_left = configuration["onlyLeft"] == "True"
            except KeyError:
                print('ERROR: config.ini가 손상되었습니다. 파일을 수정하거나 삭제 후 다시 설정해주세요.')
                close()
            
            print("\n[현재 설정]")
            print(f"백신 종류: {previous_used_type} ({next(x['name'] for x in vaccine_candidates if x['code'] == previous_used_type)})")
            print("top_x:", previous_top_x)
            print("top_y:", previous_top_y)
            print("bottom_x:", previous_bottom_x)
            print("bottom_y:", previous_bottom_y)
            print(f"only_left: {previous_only_left} ({'잔여백신이 있는 병원만 조회' if previous_only_left else '모든 병원 조회'})")
            
            while True:
                skip_input = str.lower(input("기존에 입력한 정보로 재검색하시겠습니까? Y/N : "))
                if skip_input == "y":
                    skip_input = True
                    break
                elif skip_input == "n":
                    skip_input = False
                    break
                else:
                    print("Y 또는 N을 입력해 주세요.")

            if skip_input:
                return previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y, previous_only_left

        except ValueError:
            return None, None, None, None, None, None
    return None, None, None, None, None, None


def check_user_info_loaded():
    user_info_api = 'https://vaccine.kakao.com/api/v1/user'
    user_info_response = requests.get(
        user_info_api, headers=Headers.headers_vacc, cookies=jar, verify=False)
    user_info_json = json.loads(user_info_response.text)
    if user_info_json.get('error'):
        print("사용자 정보를 불러오는데 실패하였습니다.")
        print("Chrome 브라우저에서 카카오에 제대로 로그인되어있는지 확인해주세요.")
        print("로그인이 되어 있는데도 안된다면, 카카오톡에 들어가서 잔여백신 알림 신청을 한번 해보세요. 정보제공 동의가 나온다면 동의 후 다시 시도해주세요.")
        close()
    else:
        user_info = user_info_json.get("user")
        if user_info['status'] == "NORMAL":
            print(f"[{user_info['name']}]님의 사용자 정보를 불러오는데 성공했습니다.")
        elif user_info['status'] == "UNKNOWN":
            print(f"[{user_info['name']}]님은 현재 상태를 알 수 없는 사용자입니다. 1339 또는 보건소에 문의해주세요.")
            close()
        elif user_info['status'] == "REFUSED":
            print(f"[{user_info['name']}]님은 백신을 예약하고 방문하지 않은 사용자입니다. 잔여백신 예약이 불가합니다.")
            close()
        elif user_info['status'] == "ALREADY_RESERVED" or user_info['status'] == "ALREADY_VACCINATED":
            print(f"[{user_info['name']}]님은 이미 접종이 완료되었거나 예약이 완료된 사용자입니다.")
            close()
        else:
            print(f"알려지지 않은 상태 코드입니다. 사용자명:{user_info['name']} 상태코드:{user_info['status']}")
            print("상태 코드 정보와 함께 Issues 생성 부탁드립니다.")
            close()


def set_kakao_user_cookie():
    global jar
    user_kavacto = input("카카오톡 인앱 브라우저에서 확인한 쿠키 값을 입력해주세요.\n예) VGhpcyBpcy...lNjQgc3RyaW5nLg== : ")
    jar = {'_kavacto': user_kavacto}
    dump_cookie(user_kavacto)
    
    
def dump_cookie(user_kavacto):
    config_parser = configparser.ConfigParser()
    config_parser['cookie'] = {}
    conf = config_parser['cookie']
    conf['_kavacto'] = user_kavacto
    with open("cookie.ini", "w") as cookie:
        config_parser.write(cookie)
        
        
def load_kakao_user_cookie():
    global jar
    cookie_loaded = False
    
    config_parser = configparser.ConfigParser()
    if os.path.exists('cookie.ini'):
        try:
            config_parser.read('cookie.ini')
            configuration = config_parser['cookie']
            user_kavacto = configuration["_kavacto"]
            jar = {'_kavacto': user_kavacto}
            
        except KeyError:
            print('ERROR: cookie.ini가 손상되었습니다. 파일을 수정하거나 삭제 후 다시 설정해주세요.')
            close()
        
        confirm_input = None
        while confirm_input is None:
            confirm_input = str.lower(input("기존의 사용자 정보로 진행하시겠습니까? Y/N : "))
            if confirm_input == "y":
                cookie_loaded = True
            elif confirm_input == "n":
                os.remove("cookie.ini")
                print("기존에 설정된 사용자 정보가 삭제되었습니다.")
                cookie_loaded = False
            else:
                print("Y 또는 N을 입력해 주세요.")
                confirm_input = None
    return cookie_loaded

            
def set_chrome_user_profile():
    global jar

    confirm_input = None
    while confirm_input is None:
        confirm_input = str.lower(input("Default 프로파일로 진행하시겠습니까? Y/N : "))
        if confirm_input == "y":
            return
        elif confirm_input == "n":
            profile_path = input("설정하시려는 크롬 프로파일 경로를 입력해주세요. : ")
            cookie_path = profile_path + "/Cookies"
            jar = browser_cookie3.chrome(domain_name=".kakao.com", cookie_file=cookie_path)
            dump_profile(profile_path)
        else:
            print("Y 또는 N을 입력해 주세요.")
            confirm_input = None


def load_chrome_user_profile():
    global jar
    profile_loaded = False

    config_parser = configparser.ConfigParser()
    if os.path.exists('profile.ini'):
        try:
            config_parser.read('profile.ini')
            configuration = config_parser['config']
            profile_path = configuration["profilePath"]
        except KeyError:
            print('ERROR: profile.ini가 손상되었습니다. 파일을 수정하거나 삭제 후 다시 설정해주세요.')
            close()

        print(f"기존에 설정된 크롬 프로파일 경로는\n[{profile_path}] 입니다.")

        confirm_input = None
        while confirm_input is None:
            confirm_input = str.lower(input("해당 프로파일로 진행하시겠습니까? Y/N : "))
            if confirm_input == "y":
                cookie_path = profile_path + "/Cookies"
                jar = browser_cookie3.chrome(domain_name=".kakao.com", cookie_file=cookie_path)
                profile_loaded = True
            elif confirm_input == "n":
                os.remove("profile.ini")
                print("기존에 설정된 프로파일이 삭제되었습니다.")
                profile_loaded = False
            else:
                print("Y 또는 N을 입력해 주세요.")
                confirm_input = None

    return profile_loaded


def dump_profile(profile_path):
    config_parser = configparser.ConfigParser()
    config_parser['config'] = {}
    conf = config_parser['config']
    conf['profilePath'] = profile_path

    with open("profile.ini", "w") as profile:
        config_parser.write(profile)


def check_find_vaccine_filter():
    confirm_input = None
    print("\n필터링 모드는 잔여 백신 물량이 있어도 선택하신 백신이 없는 병원을 일시적으로 자동 스킵하는 기능입니다.")
    while confirm_input is None:
        confirm_input = str.lower(input("필터링 모드를 사용하시겠습니까? (필요 없을 시 N 권장) Y/N : "))
        if confirm_input == "y":
            return True
        elif confirm_input == "n":
            return False
        else:
            print("Y 또는 N을 입력해 주세요.")
            confirm_input = None


def fill_str_with_space(input_s, max_size=40, fill_char=" "):
    """
    - 길이가 긴 문자는 2칸으로 체크하고, 짧으면 1칸으로 체크함.
    - 최대 길이(max_size)는 40이며, input_s의 실제 길이가 이보다 짧으면
    남은 문자를 fill_char로 채운다.
    """
    length = 0
    for c in input_s:
        if unicodedata.east_asian_width(c) in ["F", "W"]:
            length += 2
        else:
            length += 1
    return input_s + fill_char * (max_size - length)


def input_config():
    vaccine_type = None
    while True:
        print("\n=== 백신 목록 ===")
        for vaccine in vaccine_candidates:
            if vaccine["name"] == "(미사용)":
                continue
            print(
                f"{fill_str_with_space(vaccine['name'], 18)} : {vaccine['code']}")

        vaccine_type = str.upper(input("예약시도할 백신 코드를 알려주세요: ").strip())
        if any(x["code"] == vaccine_type for x in vaccine_candidates) or vaccine_type.startswith("FORCE:"):
            if vaccine_type.startswith("FORCE:"):
                vaccine_type = vaccine_type[6:]

                print("경고: 강제 코드 입력모드를 사용하셨습니다.\n" +
                      "이 모드는 새로운 백신이 예약된 코드로 **등록되지 않은 경우에만** 사용해야 합니다.\n" +
                      "입력하신 코드가 정상적으로 작동하는 백신 코드인지 필히 확인해주세요.\n" +
                      f"현재 코드: '{vaccine_type}'\n")

                if (len(vaccine_type) != 8 or not vaccine_type.startswith("VEN") or not vaccine_type[3:].isdigit()):
                    print("입력하신 코드가 현재 알려진 백신 코드 형식이랑 맞지 않습니다.")
                    proceed = str.lower(input("진행하시겠습니까? Y/N : "))
                    if proceed == "y":
                        pass
                    elif proceed == "n":
                        continue
                    else:
                        print("Y 또는 N을 입력해 주세요.")
                        continue

            if next((x for x in vaccine_candidates if x["code"] == vaccine_type), {"name": ""})["name"] == "(미사용)":
                print("현재 프로그램 버전에서 백신 이름이 등록되지 않은, 추후를 위해 미리 넣어둔 백신 코드입니다.\n" +
                      "입력하신 코드가 정상적으로 작동하는 백신 코드인지 필히 확인해주세요.\n" +
                      f"현재 코드: '{vaccine_type}'\n")

            break
        else:
            print("백신 코드를 확인해주세요.")

    print("\n사각형 모양으로 백신범위를 지정한 뒤, 해당 범위 안에 있는 백신을 조회해서 남은 백신이 있으면 예약을 시도합니다.")
    top_x = None
    while top_x is None:
        top_x = input("사각형의 위쪽 좌측 x값을 넣어주세요. 127.xxxxxx: ").strip()

    top_y = None
    while top_y is None:
        top_y = input("사각형의 위쪽 좌측 y값을 넣어주세요 37.xxxxxx: ").strip()

    bottom_x = None
    while bottom_x is None:
        bottom_x = input("사각형의 아래쪽 우측 x값을 넣어주세요 127.xxxxxx: ").strip()

    bottom_y = None
    while bottom_y is None:
        bottom_y = input("사각형의 아래쪽 우측 y값을 넣어주세요 37.xxxxxx: ").strip()
        
    only_left = None
    print("\n남은 잔여백신이 있는 병원만 조회할 경우 속도가 향상되나, 현재 대기중인 병원 목록을 확인할 수 없으며 리퀘스트 딜레이가 줄어들어 계정 정지의 위험이 높아집니다.")
    while only_left is None:
        only_left = str.lower(input("남은 잔여백신이 있는 병원만 조회하시겠습니까? Y/N : "))
        if only_left == "y":
            only_left = True
        elif only_left == "n":
            only_left = False
        else:
            print("Y 또는 N을 입력해 주세요.")
            only_left = None

    dump_config(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left)
    return vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left


def dump_config(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left):
    config_parser = configparser.ConfigParser()
    config_parser['config'] = {}
    conf = config_parser['config']
    conf['VAC'] = vaccine_type
    conf["topX"] = top_x
    conf["topY"] = top_y
    conf["botX"] = bottom_x
    conf["botY"] = bottom_y
    conf["onlyLeft"] = "True" if only_left else "False"

    with open("config.ini", "w") as config_file:
        config_parser.write(config_file)

        
def check_sound_file_loaded():
    not_loaded = False
    if not os.path.exists('tada.mp3'):
        print('ERROR: tada.mp3가 exe 경로에 없습니다. mp3와 exe가 같은 경로에 있는지 확인해주세요.')
        not_loaded = True
    if not os.path.exists('xylophon.mp3'):
        print('ERROR: xylophon.mp3가 exe 경로에 없습니다. mp3와 exe가 같은 경로에 있는지 확인해주세요.')
        not_loaded = True
    if not_loaded:
        input("Press Enter to close...")
        sys.exit()
        
        
def play_tada():
    try:
        mixer.init()
        mixer.music.load('tada.mp3')
        mixer.music.play()
    except:
        print("\nERROR: tada.mp3를 재생하지 못했습니다. mp3와 exe가 같은 경로에 있는지 확인해주세요.")


def play_xylophon():
    try:
        mixer.init()
        mixer.music.load('xylophon.mp3')
        mixer.music.play()
    except:
        print("\nERROR: xylophon.mp3를 재생하지 못했습니다. mp3와 exe가 같은 경로에 있는지 확인해주세요.")


def close(success=False):
    if success:
        send_msg("잔여백신 예약 성공!! \n 카카오톡지갑을 확인하세요.")
        play_tada()
    else:
        send_msg("오류와 함께 잔여백신 예약 프로그램이 종료되었습니다.")
        play_xylophon()
    input("Press Enter to close...")
    sys.exit()


class Headers:
    headers_map = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine-map.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.4.2",
        "Referer": "https://vaccine-map.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }
    headers_vacc = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.4.2",
        "Referer": "https://vaccine.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }


def try_reservation(organization_code, vaccine_type, found):
    data = {"from": "List", "vaccineCode": vaccine_type, "orgCode": organization_code, "distance": None}
    response = requests.post('https://vaccine.kakao.com/api/v2/reservation', data=json.dumps(data), headers=Headers.headers_vacc, cookies=jar, verify=False)
    print(f"{found.get('orgName')} 에서 백신을 {found.get('leftCounts')}개 발견했습니다.\n{vaccine_type} 으로 예약을 시도합니다.")
    response_json = json.loads(response.text)

    if response_json.get('error'):
        print("사용자 정보를 불러오는데 실패하였습니다.")
        print("Chrome 브라우저에서 카카오에 제대로 로그인되어있는지 확인해주세요.")
        close()
    else:
        reservation_status = response_json['code']
        
        if reservation_status == "NO_VACANCY":
            retry_reservation(organization_code, vaccine_type)
        elif reservation_status == "TIMEOUT":
            print("TIMEOUT, 예약을 재시도합니다.")
            retry_reservation(organization_code, vaccine_type)
        elif reservation_status == "SUCCESS":
            print("백신접종신청 성공!!!")
            organization_code_success = response_json.get("organization")
            print(
                f"병원이름: {organization_code_success.get('orgName')}\t" +
                f"전화번호: {organization_code_success.get('phoneNumber')}\t" +
                f"주소: {organization_code_success.get('address')}")
            close(success=True)
        else:
            print("ERROR. 아래 메시지를 보고, 예약이 신청된 병원 또는 1339에 예약이 되었는지 확인해보세요.")
            print(response.text)
            close()


def retry_reservation(organization_code, vaccine_type):
    reservation_url = 'https://vaccine.kakao.com/api/v2/reservation/retry'

    data = {"from": "List", "vaccineCode": vaccine_type,
            "orgCode": organization_code, "distance": None}
    response = requests.post(reservation_url, data=json.dumps(
        data), headers=Headers.headers_vacc, cookies=jar, verify=False)
    response_json = json.loads(response.text)
    
    if response_json.get('error'):
        print("사용자 정보를 불러오는데 실패하였습니다.")
        print("Chrome 브라우저에서 카카오에 제대로 로그인되어있는지 확인해주세요.")
        close()
    else:
        reservation_status = response_json['code']
        
        if reservation_status == "NO_VACANCY":
            print("찾으시는 백신이 없거나 선착순 마감되었습니다.")
        elif reservation_status == "SUCCESS":
            print("백신접종신청 성공!!!")
            organization_code_success = response_json.get("organization")
            print(
                f"병원이름: {organization_code_success.get('orgName')}\t" +
                f"전화번호: {organization_code_success.get('phoneNumber')}\t" +
                f"주소: {organization_code_success.get('address')}")
            close(success=True)
        else:
            print("ERROR. 아래 메시지를 보고, 예약이 신청된 병원 또는 1339에 예약이 되었는지 확인해보세요.")
            print(response.text)
            close()

# ===================================== def ===================================== #


# Get Cookie
# driver = selenium.webdriver.Firefox()
# driver.get("https://cs.kakao.com")
# pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
# cookies = pickle.load(open("cookies.pkl", "rb"))
# for cookie in cookies:
#     driver.add_cookie(cookie)
#     print(cookie)

# pylint: disable=too-many-locals,too-many-statements,too-many-branches
def find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left):
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": only_left, "order": "count",
            "topLeft": {"x": top_x, "y": top_y}}

    while True:
        try:
            response = requests.post('https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords', data=json.dumps(data), headers=Headers.headers_map, verify=False, timeout=5)
            json_data = json.loads(response.text)

            for x in json_data.get("organizations"):
                if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
                    try_reservation(x.get('orgCode'), vaccine_type, x)
                else:
                    break

            # show waiting list only when p key is pressed
            if keyboard.is_pressed("p"):
                for org in json_data["organizations"]:
                    if org.get('status') == "INPUT_YET":
                    	print(f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")

            print(f"검색 완료: {datetime.now()}")

        except json.decoder.JSONDecodeError as decodeerror:
            print("JSONDecodeError : ", decodeerror)
            print("JSON string : ", response.text)
            close()

        except requests.exceptions.Timeout as timeouterror:
            print("Timeout Error : ", timeouterror)

        except requests.exceptions.SSLError as sslerror:
            print("SSL Error : ", sslerror)
            close()

        except requests.exceptions.ConnectionError as connectionerror:
            print("Connection Error : ", connectionerror)
            # See psf/requests#5430 to know why this is necessary.
            if not re.search('Read timed out', str(connectionerror), re.IGNORECASE):
                close()

        except requests.exceptions.HTTPError as httperror:
            print("Http Error : ", httperror)
            close()

        except requests.exceptions.RequestException as error:
            print("AnyException : ", error)
            close()


def find_any_vaccine(top_x, top_y, bottom_x, bottom_y, only_left):
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": only_left, "order": "count",
            "topLeft": {"x": top_x, "y": top_y}}

    while True:
        try:
            response = requests.post('https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords', data=json.dumps(data), headers=Headers.headers_map, verify=False, timeout=5)
            json_data = json.loads(response.text)

            for x in json_data.get("organizations"):
                if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
                    organization_code = x.get('orgCode')
                    check_organization_url = f'https://vaccine.kakao.com/api/v3/org/org_code/{organization_code}'
                    check_organization_response = requests.get(check_organization_url, headers=Headers.headers_vacc, cookies=jar, verify=False)
                    check_organization_data = json.loads(check_organization_response.text).get("lefts")
                    for v in check_organization_data:
                        if v.get('leftCount') != 0:
                            try_reservation(organization_code, v.get('vaccineCode'), x)
                else:
                    break

            # show waiting list only when p key is pressed
            if keyboard.is_pressed("p"):
                for org in json_data["organizations"]:
                    if org.get('status') == "INPUT_YET":
                    	print(f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")

            print(f"검색 완료: {datetime.now()}")

        except json.decoder.JSONDecodeError as decodeerror:
            print("JSONDecodeError : ", decodeerror)
            print("JSON string : ", response.text)
            close()

        except requests.exceptions.Timeout as timeouterror:
            print("Timeout Error : ", timeouterror)

        except requests.exceptions.SSLError as sslerror:
            print("SSL Error : ", sslerror)
            close()

        except requests.exceptions.ConnectionError as connectionerror:
            print("Connection Error : ", connectionerror)
            # See psf/requests#5430 to know why this is necessary.
            if not re.search('Read timed out', str(connectionerror), re.IGNORECASE):
                close()

        except requests.exceptions.HTTPError as httperror:
            print("Http Error : ", httperror)
            close()

        except requests.exceptions.RequestException as error:
            print("AnyException : ", error)
            close()


def filter_init(vaccine_type, top_x, top_y, bottom_x, bottom_y):
    print("\n필터링을 시작합니다. 잠시만 기다려주세요.")
    filter = {}
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": True, "order": "count",
            "topLeft": {"x": top_x, "y": top_y}}

    while True:
        try:
            response = requests.post('https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords', data=json.dumps(data), headers=Headers.headers_map, verify=False, timeout=5)
            json_data = json.loads(response.text)

            for x in json_data.get("organizations"):
                left_counts = x.get('leftCounts')
                organization_code = x.get('orgCode')
                check_organization_url = f'https://vaccine.kakao.com/api/v3/org/org_code/{organization_code}'
                check_organization_response = requests.get(check_organization_url, headers=Headers.headers_vacc, cookies=jar, verify=False)
                check_organization_data = json.loads(check_organization_response.text).get("lefts")
                for v in check_organization_data:
                    if v.get('vaccineCode') == vaccine_type and v.get('leftCount') != 0:
                        try_reservation(organization_code, v.get('vaccineCode'), x)
                        left_counts -= v.get('leftCount')
                        break
                filter[organization_code] = left_counts

            break

        except json.decoder.JSONDecodeError as decodeerror:
            print("JSONDecodeError : ", decodeerror)
            print("JSON string : ", response.text)
            close()

        except requests.exceptions.Timeout as timeouterror:
            print("Timeout Error : ", timeouterror)

        except requests.exceptions.SSLError as sslerror:
            print("SSL Error : ", sslerror)
            close()

        except requests.exceptions.ConnectionError as connectionerror:
            print("Connection Error : ", connectionerror)
            # See psf/requests#5430 to know why this is necessary.
            if not re.search('Read timed out', str(connectionerror), re.IGNORECASE):
                close()

        except requests.exceptions.HTTPError as httperror:
            print("Http Error : ", httperror)
            close()

        except requests.exceptions.RequestException as error:
            print("AnyException : ", error)
            close()

    return filter
            
            
def smart_find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left, filter):
    org_filter = filter
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": only_left, "order": "count",
            "topLeft": {"x": top_x, "y": top_y}}

    while True:
        try:
            response = requests.post('https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords', data=json.dumps(data), headers=Headers.headers_map, verify=False, timeout=5)
            json_data = json.loads(response.text)

            new_org_filter = {}
            for x in json_data.get("organizations"):
                org_code = x.get('orgCode')
                left_counts = x.get('leftCounts')
                if left_counts != 0:
                    if org_filter.get(org_code, 0) != left_counts:
                        try_reservation(org_code, vaccine_type, x)
                    new_org_filter[org_code] = left_counts
                else:
                    break
            org_filter = new_org_filter
            
            # show waiting list only when p key is pressed
            if keyboard.is_pressed("p"):
                for org in json_data["organizations"]:
                    if org.get('status') == "INPUT_YET":
                    	print(f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")

            print(f"검색 완료: {datetime.now()}")

        except json.decoder.JSONDecodeError as decodeerror:
            print("JSONDecodeError : ", decodeerror)
            print("JSON string : ", response.text)
            close()

        except requests.exceptions.Timeout as timeouterror:
            print("Timeout Error : ", timeouterror)

        except requests.exceptions.SSLError as sslerror:
            print("SSL Error : ", sslerror)
            close()

        except requests.exceptions.ConnectionError as connectionerror:
            print("Connection Error : ", connectionerror)
            # See psf/requests#5430 to know why this is necessary.
            if not re.search('Read timed out', str(connectionerror), re.IGNORECASE):
                close()

        except requests.exceptions.HTTPError as httperror:
            print("Http Error : ", httperror)
            close()

        except requests.exceptions.RequestException as error:
            print("AnyException : ", error)
            close()


def main_function():
    print('* * * * * * * * * * * * * * * * * * *')
    print('*                                   *')
    print('*        KC19VR CUSTOM BUILD        *')
    print('*         v1.8  by Queue_ri         *')
    print('*                                   *')
    print('* * * * * * * * * * * * * * * * * * *\n')
    
    check_sound_file_loaded()
    
    # DEPRECATED (~21.08.19)
    # profile_loaded = load_chrome_user_profile()
    # if profile_loaded is False:
    #     set_chrome_user_profile()
    
    cookie_loaded = load_kakao_user_cookie()
    if cookie_loaded is False:
        set_kakao_user_cookie()
    
    check_user_info_loaded()
    
    previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y, previous_only_left = load_config()
    if previous_used_type is None:
        vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left = input_config()
    else:
        vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left = previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y, previous_only_left
    
    if vaccine_type == "ANY":
        find_any_vaccine(top_x, top_y, bottom_x, bottom_y, only_left)
    else:
        apply_filter = check_find_vaccine_filter()
        if apply_filter:
            filter = filter_init(vaccine_type, top_x, top_y, bottom_x, bottom_y)
            smart_find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left, filter)
        else:
            find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left)
    close()


def send_msg(msg):
    config_parser = configparser.ConfigParser()
    if os.path.exists('telegram.txt'):
        try:
            config_parser.read('telegram.txt')
            print("Telegram으로 결과를 전송합니다.")
            tgtoken = config_parser["telegram"]["token"]
            tgid = config_parser["telegram"]["chatid"]
            bot = telepot.Bot(tgtoken)
            bot.sendMessage(tgid, msg)
            return
        except Exception as e:
            print("Telegram Error : ", e)
            return


# ===================================== run ===================================== #
if __name__ == '__main__':
    main_function()
