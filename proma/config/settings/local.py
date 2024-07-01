from .base import *
# 로컬 환경에서 구동하는 명령어
# python manage.py runserver --settings=config.settings.local

# 장고 실행시 사용하는 setting파일에 대한 환경변수
# set DJANGO_SETTINGS_MODULE=config.settings.local
# python manage.py runserver

ALLOWED_HOSTS = []