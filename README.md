# Pool Backend

A FastAPI-based backend for the Pool application.

## Features

- FastAPI framework
- SQLAlchemy ORM
- Alembic migrations
- JWT authentication
- PostgreSQL database
- Poetry dependency management
- Docker Compose for database
- React/TypeScript frontend with shadcn/ui

## Quick Start

### Single Command (Recommended)

Start both backend and frontend with one command:

```bash
npm run dev
```

This will start:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

### Manual Setup

#### Option 1: Using Docker Compose (Recommended)

1. Start the PostgreSQL database:
```bash
docker-compose up -d postgres
```

2. Install all dependencies:
```bash
npm run install:all
```

3. Set up environment variables:
```bash
cp env.example .env
```

4. Run database migrations:
```bash
poetry run alembic upgrade head
```

5. Start both servers:
```bash
npm run dev
```

#### Option 2: Local PostgreSQL

1. Install and start PostgreSQL locally
2. Create a database and update the `DATABASE_URL` in your `.env` file
3. Follow steps 2-5 from Option 1

## Development

- Run tests: `poetry run pytest`
- Format code: `poetry run black .`
- Sort imports: `poetry run isort .`
- Lint code: `poetry run flake8 .`
- Type checking: `poetry run mypy .`

## Database Management

- Create a new migration: `poetry run alembic revision --autogenerate -m "description"`
- Apply migrations: `poetry run alembic upgrade head`
- Rollback migration: `poetry run alembic downgrade -1`

## Docker Commands

- Start database: `docker-compose up -d postgres`
- Stop database: `docker-compose down`
- View logs: `docker-compose logs postgres`
- Reset database: `docker-compose down -v && docker-compose up -d postgres`

## Available Scripts

- `npm run dev` - Start both backend and frontend
- `npm run dev:backend` - Start only the backend
- `npm run dev:frontend` - Start only the frontend
- `npm run install:all` - Install all dependencies (Poetry + npm) 