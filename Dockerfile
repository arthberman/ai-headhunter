FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
  libpq-dev \
  gcc \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.3.3 /uv /bin/uv

# Copy the project into the image
ADD . /app
WORKDIR /app

# Sync the project into a new environment, using the frozen lockfile
RUN uv sync --frozen

# Use the virtual environment automatically
ENV VIRTUAL_ENV=/app/.venv
# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

COPY .env .

CMD ["uv", "run", "src/server.py"]