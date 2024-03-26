# Python IDE Setting for windows (with. pyenv)
참조: [pyenv-win.git](https://github.com/pyenv-win/pyenv-win/blob/master/README.md#installation)
## A. pyenv 설치
- 윈도우 용 pyenv 설치는 mac os에 비해 복잡하지만 의외로 쉽다.
- 아래 순서로 pyenv 설치 및 환경 변수 설정까지 마치면 개발환경(IDE)관리가 쉬워진다.

#### 1. 관리자 권한으로 PowerShell 실행
- "win" 키 > "PowerShell" 검색 > 우클릭 후 관리자 권한으로 실행 선택   

#### 2. pyenv-win install
- 아래 명령어 복사>붙여넣기 후 실행
```shell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```
#### 3. PowerShell 다시시작

#### 4. ```pyenv --version``` 실행하여 설치 여부 확인

#### 5. 환경 변수 설정
- "win" 키 > "시스템 환경 변수 편집" 검색 > 창 하단 "환경 변수" 선택 > 시스템 변수 "새로 만들기" 선택
- 아래 두 가지를 추가한다.  
변수 이름: ```PYENV```
변수 값: ```C:\Users\사용자ID\.pyenv\pyenv-win\bin```   
변수 이름: ```PYENV_HOME```
변수 값: ```C:\Users\사용자ID\.pyenv\pyenv-win\```   
- 환경 변수가 이미 설정되어 있다면 건드릴 필요 없다.
#### 6. ```pyenv version``` 실행
- pyenv 버전과 설치경로가 출력된다면 성공

## B. Python 설치
- 앞서 설치한 pyenv를 활용해 가상환경까지 만드는 것을 목표로 실습할 예정
- 앞으로 파이썬을 활용한 프로젝트를 진행하면서 여러 파이썬 버전과 라이브러리들을 설치하고 지우게 될 텐데 이를 **가상 환경**만들어 보다 쉽게 관리할 수 있게 된다.
#### 1. CMD 또는 PowerShell 실행
#### 2. pyenv install -l 실행
- 이를 통해 설치 가능한 모든 python 리스트를 확인할 수 있다.
- 의미 없어 보일 수는 있는데 pyenv 설치 이후 파이썬 설치시 꼭 한번은 실행해야 된다.
#### 3. pyenv install "version"
- 원하는 버전의 python 버전 번호를 입력한다. (""는 입력 시 생략)
- 만약 원하는 python 버전이 python 3.9.9 라면 ```pyenv install 3.9.9``` 입력 후 실행
#### 4. pyenv global "version"
- 설치한 python들 중 원하는 버전의 python을 전역 버전으로 설정한다.
- 이렇게 하면 가상환경 생성 시 기본 python 버전을 설정한 것이 된다.
- 이후 pyenv 명령어를 통해 가상환경 생성 후 원하는 python 버전을 설정하면 된다.
#### Python 작동 확인
```shell
python -c "import sys; print(sys.executable)"
```
- 위 명령어 실행 후 pyenv 설치 경로와 python 설치경로가 잘 표시된다면 성공

## C. 가상환경 세팅하기
- mac os 에서는 pyenv 설치 시 **"pyenv-virtualenv"**가 함께 설치되어 가상환경 관리가 쉽다고 한다.
- 어떻게든 pyenv-virtualenv를 windows 환경에서 사용해보고자 삽질해 봤지만 방법은 없는 것 같다. [설치관련 정보](https://github.com/pyenv/pyenv-virtualenv)
- pyenv-virtualenv 없이 python의 **"venv"** 명령어를 활용해 가상환경을 관리하는 방법을 사용하려고 한다. [pyenv-virtualenv를 활용한 가상 환경 관리](https://deku.posstree.com/ko/environment/pyenv/#pyenv-virtualenv-%EC%84%A4%EC%B9%98)

#### 1. 프로젝트 디렉토리로 이동
- 터미널 실행 후 ```cd 프로젝트 디렉토리```명령어 실행하여 디렉토리 이동 후 아래 명령어 실행
```
python -m venv "가상환경 디렉토리 이름"
```
- .venv 로 디렉토리 이름을 정하는게 관행임으로 어느정도 차용할 필요는 있어 보인다.
#### 2. .gitignore 추가 (선택)
- 가상 환경을 굳이 git과 같은 소스 버전에 관리 시스템에 올릴 필요는 없다.
- 버전 관리 시스템으로 관리가 필요하다면 진행하지 않아도 된다.

#### 3. 가상환경 활성화
- 터미널에서 아래 명령어 실행
```shell
.가상환경이름\Scripts\activate.bat
```
- 아래 명령어로 활성화 여부 확인가능
```shell
where python
C:\...
E:\...\.venv_LearnPy\Scripts\python.exe  #프로젝트 디렉토리에 python 정보 확인가능
C:\...
```
