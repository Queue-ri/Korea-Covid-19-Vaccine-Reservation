# 💉 Korea-Covid-19-Vaccine-Reservation
![Kakao](https://img.shields.io/badge/Kakao-ffcd00.svg?style=flat&logo=kakao&logoColor=000000) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![latest release](https://img.shields.io/github/v/release/Queue-ri/Korea-Covid-19-Vaccine-Reservation)](https://github.com/Queue-ri/Korea-Covid-19-Vaccine-Reservation/releases) [![Python Lint](https://github.com/Queue-ri/Korea-Covid-19-Vaccine-Reservation/actions/workflows/python-lint.yml/badge.svg)](https://github.com/Queue-ri/Korea-Covid-19-Vaccine-Reservation/actions/workflows/python-lint.yml)

[코로나 잔여 백신 예약 매크로](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro)를 기반으로 한 커스텀 빌드입니다.

**더 빠른 백신 예약을 목표로 하며, 속도를 우선하기 때문에 사용자는 이에 대처가 가능해야 합니다.**

지정한 좌표 내 대기중인 병원에서 잔여 백신이 확인될 시 설정한 백신 종류로 예약을 시도합니다.

## 📌 변경 사항
### 속도 향상
- **request delay가 없습니다. 주의해주세요.** *(변경 전: 200ms)*
- 예약 실패 시의 delay가 없습니다. *(변경 전: 80ms)*
- 대기 중인 병원 리스트는 `p` 키를 누를 시에만 출력됩니다. *(변경 전: 항상 출력)*
- 잔여 백신 발견 시, 우선 예약 시도 후 발견 안내문을 출력합니다. *(변경 전: 안내문 출력 후 예약 시도)*
- `ANY` 옵션의 로직을 분리하여 프로시저를 간소화합니다. v1.3부터 지원됩니다. *(변경 전: 분리되지 않음)*
- 잔여 백신이 있는 병원이 여러 곳일 때, 한 곳의 예약이 실패해도 바로 다음 병원에 예약을 시도합니다. *(변경 전: 다음 병원 스킵)*
- 잔여 백신 물량이 많은 순으로 예약을 시도하고, 물량이 없다면 `break` 후 서버에 다시 요청합니다. *(변경 전: `break` 없음)*

### UI/UX
- **`Default`가 아닌 크롬 프로파일을 지원합니다.** (v1.6 부터 지원)
- **잔여 백신이 있어도 선택한 백신이 없는 병원을 일시적으로 스킵하는 필터링 모드를 지원합니다.** (v1.7 부터 지원)
- `playsound`가 불안정하여 mp3 경로 수정 및 라이브러리를 변경했습니다. 하단의 **주의 사항**을 참고해주세요.
- 편의를 위해 연동된 카카오 사용자명이 출력됩니다.
- 실행 시 커스텀 빌드 안내용 배너가 출력됩니다. (버전은 v1.5부터 표시됩니다.)
```
* * * * * * * * * * * * * * * * * * *
*                                   *
*        KC19VR CUSTOM BUILD        *
*         v1.x  by Queue_ri         *
*                                   *
* * * * * * * * * * * * * * * * * * *
```

### 코드 정리
- 잔여 백신 존재 병원이 None인지 검사하는 구문이 제거되었습니다.
- `find_vaccine`에서의 `while` 문을 `break` 하지 않고 바로 `try_reservation`을 호출합니다.
- `try_reservation` 호출 단의 조건문이 제거되었으며, response 파싱 로직이 간소화되었습니다.
- `clear`, `resource_path` 함수가 제거되었습니다.

## 📌 이용 방법
### 기본 사용법
1. [카카오 사용자 쿠키 찾는법](https://github.com/Queue-ri/Korea-Covid-19-Vaccine-Reservation/blob/main/docs/cookie-manual.md)을 참고하여 프로그램에 백신을 예약할 카카오 계정을 연동합니다.
2. [좌표 값 찾는법](https://github.com/Queue-ri/Korea-Covid-19-Vaccine-Reservation/blob/main/docs/coords-manual.md)을 참고하여 탐색할 범위의 좌표를 알아둡니다.
3. `pyinstaller`로 `cb.py`를 빌드합니다. **더 빠른 성능을 원할 경우 `nuitka`로 빌드합니다.** [(빌드 방법)](https://github.com/Queue-ri/Korea-Covid-19-Vaccine-Reservation/blob/main/docs/build-manual.md)
4. 백신 코드, 좌표, 옵션이 입력되면 자동 예약을 시도합니다. 이전 설정(`config.ini`)이 있다면 해당 설정을 재사용할 수 있습니다.
5. 예약 성공 시 빵빠레 소리와 함께 예약이 성공했음이 안내됩니다.

### 텔레그램으로 결과 전송하기
1. 다음의 내용으로 `telegram.txt`를 작성합니다. [(추가 설명)](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/discussions/574)
```
[telegram]
token = 토큰값
chatid = 채팅방ID
```
2. `exe` 실행 전 `telegram.txt`는 `exe`와 같은 경로에 위치해야 합니다.

## 📌 주의 사항
- **프로그램을 동시에 너무 많이 실행하면 카카오 계정이 정지될 수 있습니다.**
- 오류가 발생하거나 예약에 성공한 경우 프로그램이 자동 종료됩니다.
- 예약 시도가 반드시 성공한다는 보장은 없습니다.
- **실행 전, `exe` 파일이 `mp3` 파일과 같은 경로에 위치해야 합니다.**
- tmux, screen과 같은 터미널 멀티플렉싱 프로그램이 자동으로 실행되지 않아야 합니다.
- 바이러스가 탐지될 시 이는 오진(false positive)입니다.

## 📌 Disclaimer
- 본 프로그램은 매크로를 이용한 백신 예약을 유도하는 내용이 아니며, 해당 프로그램을 사용함으로서 생기는 책임은 모두 이용자 본인에게 있습니다.
