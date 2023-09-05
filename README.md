# WeGoGym-api
## Initial Setup
### Install Python env and dependencies

처음 FastAPI 개발 환경 세팅하기

[poetry 설치](https://python-poetry.org/docs/#installation)

프로젝트 루트 경로에서 가상환경 생성 및 패키지 설치

```bash
poetry install
```

가상환경 활성화

```bash
poetry shell
```

기타 명령어는 [poetry 공식 문서](https://python-poetry.org/docs/basic-usage/) 참조

### IDE setting
#### VSCode

`.vscode/settings.json` 파일을 생성하고 아래의 내용을 붙여넣기 함.

```json
{
  "python.linting.mypyEnabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": false,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

## Docker
실제 개발 환경 및 배포 환경은 도커라이징 되어 있음.
따라서 도커를 설치하여 `docker compose` 명령어를 실행하여야 함.
도커 compose v1의 경우 `docker-compose` 명령어를 사용함.
### Local
로컬 환경에서. docker-compose.local.yaml 파일을 사용하여 빌드 및 실행함.
레디스, db만 도커 이용.
```sh
docker compose -f docker-compose.local.yaml up -d --build 
uvicorn app.main:app --reload --log-level debug --host 0.0.0.0 --port 8000
```

```sh
### Production

ec2 환경에서. docker-compose.prod.yaml 파일을 사용하여 빌드 및 실행함.

```sh
docker compose -f docker-compose.prod.yaml up -d --build
```

### Build
- `docker compose up --build`: 코드 변경이 있는 경우, 다시 빌드하고 컨테이너를 실행함.

### Run
- `docker compose up`: 도커 컨테이너를 실행함. 빌드가 안되어 있다면 처음에 한 번 빌드 진행함.

### Stop
- `docker compose down`: 도커 컨테이너를 종료함.
- `docker compose down -v`: 도커 컨테이너를 종료하고, volume도 함께 삭제함.

자세한 옵션은 [링크](https://docs.docker.com/engine/reference/commandline/compose_down/) 참조.

## Local Development
도커 db, redis 컨테이너를 실행한 상태에서 아래의 명령어를 실행하여 개발을 진행함. [로컬 도커파일](#local)

레디스 클러스터 장애발생시 도커 파일 재시작 필요함.

### Install Dependencies
```bash
poetry install
```

### Run

```bash
poetry shell
```

```bash
uvicorn app.main:app --reload --host 0.0.0.0
```
### Test
```bash
pytest
```
### Lint
```bash
flake8 app
mypy app
```
### Format
```bash
black app
```


## Migration (Alembic)
### Make Migration

```bash
alembic revision --autogenerate -m "type your commit message"
```
이후에 versions에 migration 히스토리 저장됨.
### Migrate
이 명령어는 실질적으로 사용할 일은 없음. `docker compose up --build` 명령어 실행시 자동으로 실행되도록 설정되어 있음.
```bash
alembic upgrade head
```
### Downgrade
```bash
alembic downgrade -1
```

