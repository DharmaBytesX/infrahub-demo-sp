# Batfish runner sidecar image.
#
# The build context is the repository root, because the image also carries the
# Batfish helpers from `checks/`:
#
#   docker build -f batfish_runner/Dockerfile -t infrahub-demo-sp-batfish-runner .
#
# Published as registry.opsmill.io/opsmill/infrahub-demo-sp-batfish-runner.
FROM python:3.12-slim

# Same uv version as the CI workflows (UV_VERSION in .github/workflows/ci.yml).
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /usr/local/bin/uv

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app

WORKDIR /app

# Install only what the runner needs, at the versions pinned in uv.lock.
COPY pyproject.toml uv.lock /tmp/lock/
COPY batfish_runner/requirements.txt /tmp/requirements.txt
RUN uv export --frozen --no-dev --no-hashes --no-emit-project \
        --directory /tmp/lock --output-file /tmp/constraints.txt \
    && uv pip install --system --no-cache \
        --requirement /tmp/requirements.txt --constraint /tmp/constraints.txt \
    && rm -rf /tmp/lock /tmp/requirements.txt /tmp/constraints.txt

COPY --chown=app:app batfish_runner/app.py ./
COPY --chown=app:app checks/__init__.py checks/batfish_common.py checks/batfish_helpers.py ./checks/

USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=5 \
  CMD curl --fail http://localhost:8080/health || exit 1

CMD ["python", "app.py"]
