# WeGoGym-api
## Initial Setup
### Install Python env
처음 FastAPI 개발 환경 세팅하기

```bash
$ brew install openssl readline sqlite3 xz zlib
```

```bash
$ brew install pyenv
```

```bash
$ vi ~/.profile
```

~/.bashrc 를 포함한 블록이 나오기 전에 

```bash
export PYENV_ROOT="$HOME/.pyenv"

export PATH="$PYENV_ROOT/bin:$PATH"

eval "$(pyenv init --path)"
```

아래의 코드 추가 후 저장하기

```bash
$ vi ~/.zshrc
```

맨 마지막 라인 밑에 

```bash
eval "$(pyenv init -)"

```

추가 후 저장.

M1 맥의 경우 zshrc에 bzip 관련 설정 추가하기
```bash
export LDFLAGS="-L/opt/homebrew/opt/bzip2/lib"
export CPPFLAGS="-I/opt/homebrew/opt/bzip2/include"
```

```bash
$ source ~/.profile && exec $SHELL
```

실행

```bash
$ pyenv install 3.9.13
```

```bash
pyenv global 3.9.13
```

과 같이 전역에서 사용할  버전 지정가능

파이썬 가상환경 생성 방법

```bash
python -m venv ./venv
```

프로젝트 코드의 루트 경로에서 실행. venv가 아닌 다른 이름으로 지정해도 괜찮음

```bash
source venv/bin/activate
```

로 가상환경 활성화

## Docker
실제 개발 환경 및 배포 환경은 도커라이징 되어 있음.
따라서 도커를 설치하여 `docker compose` 명령어를 실행하여야 함.
도커 compose v1의 경우 `docker-compose` 명령어를 사용함.
### Production

ec2 환경에서. docker-compose.prod.yaml 파일을 사용하여 빌드 및 실행함.

```sh
$ docker compose -f docker-compose.prod.yaml up -d --build
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
도커 db, redis 컨테이너를 실행한 상태에서 아래의 명령어를 실행하여 개발을 진행함.
### Install Dependencies
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Run
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
> 주의사항: `.env`에서 `ENVIRONMENT=DEV`로 설정되어 있어야 함. 추후에 자동적으로 설정되도록 변경 예정. docker 컨테이너 내부의 DB 이미지 실행 중이어야 함.

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

