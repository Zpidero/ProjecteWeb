FROM astral/uv:python3.12-bookworm-slim

WORKDIR /app
ADD uv.lock uv.lock
ADD pyproject.toml pyproject.toml
RUN uv sync

COPY . .
EXPOSE 8000

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]