# CLAUDE.md

이 파일은 royt 핫튜브 프로젝트의 개발문서입니다.

## 프로젝트 개요

"royt" (핫튜브)는 Django 기반의 API 게이트웨이 프로젝트입니다. Docker로 컨테이너화되어 있으며 여러 환경(local, dev, staging, prod)에서 실행되도록 설계되었습니다.

## 유의사항
- 사용할 API의 Wrapper 클래스를 먼저 만듭니다.
- 이 래퍼 클래스를 이용해서 실행할 커맨드를 만듭니다. 이 커맨드는 `youtube/management/commands/`에 위치해야 합니다.
  - 이 커맨드의 목적은 래퍼가 잘 실행되는지 확인하기 위한 것이며 유튜브 API 호출 결과를 최대한 그대로 보여주는 것이 목적입니다. 또한 호출 결과를 잘 사용할 수 있도록 시리얼라이즈합니다.
- 자동테스트, 유닛테스트는 작성하지 않습니다. 제가 직접 장고 커맨드를 사용하여 테스트할 예정입니다.
- 항상 API 할당량을 최소한 사용하는 방법으로 코드를 작성해야 합니다.

## 생각
- 클로드를 이용한 자막 정리는 굳이 할 필요가 없다.

## 아키텍처

### 핵심 구조

- **ms_skeleton**: Django 프로젝트 루트 (settings 및 URL 설정 포함)
- **base**: 앱 전체에서 공통으로 사용하는 추상 베이스 모델 (`RoBase`, `LogBase`, `Chory`, `Comment`, `Like`) 포함
- **common**: 공유 유틸리티 및 커스텀 구현
  - `common/custom/`: 커스텀 Django 컴포넌트 (데이터베이스 라우터, JWT 시리얼라이저, 파서)
  - `common/util/`: 유틸리티 모듈 (AWS, 지리정보, 로깅, 시리얼라이저 등)
- **config**: 애플리케이션 설정 관리
- **user**: 사용자 인증 및 관리 (CustomUser 모델 사용)

### 데이터베이스 아키텍처

- 기본 데이터베이스로 SQLite3 사용
- `common/custom/CustomRouter.py`를 통한 다중 데이터베이스 라우팅 지원
- Django settings 모듈은 `ms_skeleton.settings` 참조
- 데이터베이스 파일 저장 위치: `/usr/data/{PROJECT_NAME}{RUNNING_ENV}/`

### API 구조

- 모든 API 엔드포인트는 `/api/` 접두사 사용
- 관리자 패널: `/{ADMIN_PREFIX}/` (기본값: `adminachy`)
- Django REST Framework와 JWT 인증(djangorestframework-simplejwt) 사용
- drf-yasg를 사용한 Swagger/OpenAPI 문서화 (현재 urls.py에서 주석 처리됨)

### 환경 설정

프로젝트는 `.env` 파일의 환경 변수를 사용합니다:
- `PROJECT_NAME`: 프로젝트 식별자 (예: "royt")
- `SERVICE_NAME`: 표시 이름 (예: "핫튜브")
- `RUNNING_ENV`: 실행 환경 (local/dev/staging/prod)
- `DEBUG`: 디버그 모드 토글
- `SECRET_KEY`: Django 시크릿 키
- JWT 토큰 수명, AWS 자격 증명, Slack/Telegram 연동 설정 등

## 개발 명령어

### 로컬 개발

**로컬에서 빌드 및 실행:**
```bash
./shell/build-local.sh
```
이 스크립트는:
1. `.env` 파일을 `docker/` 및 `api-gateway/`로 복사
2. Docker 컨테이너 빌드
3. 기존 컨테이너 중지
4. 애플리케이션 시작

**Docker Compose (수동):**
```bash
# 빌드
docker-compose -p royt -f docker/docker-compose.local.yml --env-file .env build

# 시작
docker-compose -p royt -f docker/docker-compose.local.yml up

# 중지
docker-compose -p royt -f docker/docker-compose.local.yml down --remove-orphans
```

**애플리케이션 접근:**
- Backend API: http://localhost:5100
- 컨테이너 내부에서는 8000번 포트로 실행되며, 호스트의 `BE_PORT`(5100)로 매핑됨

### Django 관리 명령어

**마이그레이션 실행:**
```bash
docker exec -it <container-name> ./manage.py migrate
```

**슈퍼유저 생성:**
```bash
docker exec -it <container-name> ./manage.py createsuperuser
```

**정적 파일 수집:**
```bash
docker exec -it <container-name> ./manage.py collectstatic
```

**Django 셸 실행:**
```bash
docker exec -it <container-name> ./manage.py shell
```

**테스트 실행:**
```bash
docker exec -it <container-name> ./manage.py test
```

## 주요 기술 사항

### 인증
- API 인증에 JWT (Simple JWT) 사용
- 커스텀 유저 모델: `user.CustomUser`
- 이메일 기반 인증 (username 필드 없음)
- Access 토큰 수명: `JWT_ACCESS_TOKEN_LIFETIME_MIN`으로 설정
- Refresh 토큰 수명: `JWT_REFRESH_TOKEN_LIFETIME_MIN`으로 설정

### 스토리지
- django-storages를 사용한 AWS S3 연동
- S3 버킷 설정: `AWS_STORAGE_BUCKET_NAME`
- 업로드 경로: `{PROJECT_NAME}/{RUNNING_ENV[0].lower()}`

### 로깅
- 로그 저장 위치: `/usr/log/{PROJECT_NAME}{RUNNING_ENV}/`
- 메인 로그 파일: `django-all.log`
- Rotating file handler (파일당 5 MB, 99개 백업)

### CORS
- `CORS_ORIGIN_WHITELIST` 환경 변수로 설정
- Sentry trace 지원을 포함한 커스텀 CORS 헤더

### 베이스 모델 패턴
모든 Django 앱은 `base/models.py`의 추상 베이스 모델을 상속해야 합니다:
- `RoBase`: created_date, created_at, updated_at 포함 표준 모델
- `LogBase`: job_id 및 tag 필드가 있는 로깅 모델용
- `Chory`: owner, title, content가 있는 컨텐츠 아이템용
- `Comment`: 댓글 기능용
- `Like`: 좋아요/반응 기능용

모든 베이스 모델은 인스턴스를 딕셔너리로 변환하는 `to_obj` 프로퍼티를 포함합니다.

### 알림 연동
- Slack: 웹훅 및 봇 토큰 사용
- Telegram: 알림용 봇 연동
- `MSG_TARGET` 환경 변수로 대상 설정

## Docker 환경

프로젝트는 다양한 환경을 위한 여러 Dockerfile을 지원합니다:
- `Dockerfile.local`: 로컬 개발 (Python 3.10-slim)
- `Dockerfile.dev`: 개발 서버
- `Dockerfile.staging`: 스테이징 환경
- `Dockerfile.prod`: 프로덕션 배포

각 환경마다 `api-gateway/docker/`에 대응하는 entrypoint 스크립트가 있습니다.
