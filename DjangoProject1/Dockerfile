FROM astral/uv:python3.14-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sLo /usr/local/bin/tailwindcss \
    "https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.17/tailwindcss-linux-x64" \
    && chmod +x /usr/local/bin/tailwindcss

WORKDIR /app

COPY uv.lock pyproject.toml ./
RUN uv sync --no-install-project --frozen

COPY . .

EXPOSE 8080

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8080"]


# release CMD :

    # CMD ["sh", "-c", "uv run manage.py migrate && uv run manage.py sync_players && uv run manage.py runserver 0.0.0.0:8080"]