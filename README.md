# devops-cicd-lab

[![CI Pipeline](https://github.com/D4NDy7/lab_CI-CD/actions/workflows/ci.yml/badge.svg)](https://github.com/D4NDy7/lab_CI-CD/actions/workflows/ci.yml)

> **Лабораторная работа № 7 — CI/CD Pipeline на GitHub Actions**
> Курс: DevOps и инфраструктура | Уровень: Магистратура

---

## Что реализовано

| Паттерн | Файл | Описание |
|---|---|---|
| Diamond Pipeline | `.github/workflows/ci.yml` | build → \[lint, test, security-scan\] → quality-gate → docker-build |
| Promotion Pipeline | `.github/workflows/cd.yml` | staging → smoke-test → production (с approval) |
| Trunk-Based Dev | Branch protection + PR flow | Все изменения через PR, quality-gate как required check |
| Feature Flag | `GET /greeting` + env var | `FEATURE_NEW_GREETING=true/false` |
| Build Once Deploy Many | CI пушит SHA-тег, CD только деплоит | Никакой пересборки в CD |

---

## Структура проекта

```
devops-cicd-lab/
├── app/
│   ├── src/
│   │   └── app.py            # Flask-приложение (3 эндпоинта)
│   ├── tests/
│   │   └── test_app.py       # 4 unit-теста (pytest)
│   ├── Dockerfile            # Multi-stage build
│   ├── requirements.txt      # Flask, gunicorn
│   ├── requirements-dev.txt  # pytest, ruff
│   └── pyproject.toml        # ruff + pytest config
├── .github/
│   └── workflows/
│       ├── ci.yml            # CI: Diamond Pattern (6 jobs)
│       └── cd.yml            # CD: Promotion Pattern (3 jobs)
├── .gitignore
└── README.md
```

---

## API эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/` | `{ service, version, hostname }` |
| GET | `/health` | `{ status: "ok" }` |
| GET | `/greeting` | Зависит от `FEATURE_NEW_GREETING` |

---

## Локальный запуск

```bash
# Установка зависимостей
cd app
pip install -r requirements.txt -r requirements-dev.txt

# Линтер
ruff check src/ tests/

# Тесты
pytest tests/ -v

# Запуск приложения
python src/app.py

# Feature flag включён
FEATURE_NEW_GREETING=true python src/app.py
```

### Docker

```bash
cd app
docker build -t devops-cicd-lab:local .
docker run -p 8080:8080 devops-cicd-lab:local

# Проверка
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/greeting

# С feature flag
docker run -p 8080:8080 -e FEATURE_NEW_GREETING=true devops-cicd-lab:local
curl http://localhost:8080/greeting
```

---

## CI Pipeline (Diamond Pattern)

```
push/PR → build
               ├── lint          ┐
               ├── test          ├── (параллельно, Fan-Out)
               └── security-scan ┘
                       ↓
                 quality-gate    (Fan-In)
                       ↓
                 docker-build    (только main, SHA-тег)
```

Особенности:
- Кэширование pip зависимостей (`actions/setup-python cache: pip`)
- Docker layer cache (`type=gha`)
- Тег образа: `sha-<full-sha>` (не `:latest`)
- Результаты тестов сохраняются как артефакты (`if: always()`)

---

## CD Pipeline (Promotion Pattern)

```
CI success → deploy-staging → smoke-test → deploy-production
                                               ↑
                                         (ручной approval)
```

- `staging` — автодеплой без ограничений
- `production` — Required Reviewers (Settings → Environments)

---

## Настройка репозитория

### 1. GitHub Environments

Перейди в **Settings → Environments**:

- **staging** — без ограничений
- **production** — добавь себя в Required Reviewers

### 2. Branch Protection

**Settings → Branches → Add rule** для `main`:

- [x] Require a pull request before merging
- [x] Require status checks to pass → добавь `Quality Gate`
- [x] Require branches to be up to date before merging
- [x] Do not allow bypassing the above settings

### 3. Обнови badge в README

Замени `YOUR_USERNAME` на свой GitHub username.

---

## TBD-цикл (Задание 4.3)

```bash
# 1. Создай ветку
git checkout -b feat/greeting

# 2. Код + тесты уже есть, можно добавить что-то своё
# ...

# 3. Conventional commit
git add .
git commit -m "feat: add greeting endpoint with feature flag"
git push origin feat/greeting

# 4. Открой PR → дождись зелёного quality-gate → смержи
# 5. CD запустится автоматически → подтверди деплой в production
```

---

## Чеклист (100 + 10 баллов)

### CI Pipeline (40 баллов)
- [x] Пайплайн на push в main и pull_request
- [x] lint, test, security-scan параллельно (Fan-Out)
- [x] quality-gate ждёт всех трёх (Fan-In)
- [x] Docker-образ в ghcr.io с SHA-тегом
- [x] Docker layer cache (type=gha)
- [x] Кэширование pip зависимостей
- [x] Результаты тестов как артефакты (if: always())
- [x] Conventional Commits

### CD Pipeline (25 баллов)
- [x] CD после успешного CI (workflow_run)
- [x] GitHub Environments (staging + production)
- [x] Staging автодеплой
- [x] Production с ручным подтверждением
- [x] Smoke test между staging и production

### Trunk-Based Development (25 баллов)
- [x] Branch protection на main
- [x] quality-gate как required status check
- [x] Feature flag через переменную окружения
- [x] Тесты на оба варианта feature flag
- [x] PR с пройденным CI в истории

### Бонус (+10 баллов)
- [ ] Matrix build (несколько версий Python)
- [ ] Reusable workflow
- [x] CI status badge в README
- [ ] Dependabot

---

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [docker/build-push-action](https://github.com/docker/build-push-action)
- [Trunk Based Development](https://trunkbaseddevelopment.com)
- [Conventional Commits](https://www.conventionalcommits.org)
