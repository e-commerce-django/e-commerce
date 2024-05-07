# e-commerce
techit 2차 이커머스 프로젝트 저장소 입니다.


# 구성원
조준호: 팀장  
강민수: 백엔드  
신현수: 백엔드  
이소현: 프론트엔드  


# 아이디어
경매 서비스를 제공하는 개인 거래 사이트

<br>

비슷한 사이트 👉 [collex](https://auction.collexx.io/bid?category=1&sortBy=deadLineTime%3AASC)


# 스택
## Backend
python, django, postgresql


## Frontend
html, css, django-template


# 개발 방법
## branch 관리
`issue` 생성 및 issue number로 branch 생성  

# 실행 순서
python manage.py runserver
celery -A config worker --loglevel=INFO -P solo #상품 상태 업데이트를 위한 서버를 여는 명령어입니다.
celery -A config beat -l info #주기적 작업을 서버에 요청하는 명령어입니다.
세 가지 전부 실행되어야 서비스를 원활하게 이용할 수 있습니다.


## install requirements.txt 
```
$ pip install -r requirements.txt
```
- `requirements.txt` 파일에 명시된 라이브러리를 설치합니다.  