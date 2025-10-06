FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./

RUN uv pip install --system -r pyproject.toml

COPY . .

CMD ["uv", "run", "python", "-m", "psychohelp.main"]