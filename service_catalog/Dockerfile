# Streamlit Service Catalog image.
#
# The build context is the repository root, because the image also carries the
# Batfish helpers from `checks/`:
#
#   docker build -f service_catalog/Dockerfile -t infrahub-demo-sp-streamlit .
#
# Published as registry.opsmill.io/opsmill/infrahub-demo-sp-streamlit.
FROM python:3.12-slim

# Same uv version as the CI workflows (UV_VERSION in .github/workflows/ci.yml).
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /usr/local/bin/uv

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app

WORKDIR /app

# Install only what the catalog needs, at the versions pinned in uv.lock, so the
# image matches what the integration tests ran against.
COPY pyproject.toml uv.lock /tmp/lock/
COPY service_catalog/requirements.txt /tmp/requirements.txt
RUN uv export --frozen --no-dev --no-hashes --no-emit-project \
        --directory /tmp/lock --output-file /tmp/constraints.txt \
    && uv pip install --system --no-cache \
        --requirement /tmp/requirements.txt --constraint /tmp/constraints.txt \
    && rm -rf /tmp/lock /tmp/requirements.txt /tmp/constraints.txt

COPY --chown=app:app service_catalog/ ./
# The Batfish Check page imports `checks.batfish_helpers`.
COPY --chown=app:app checks/__init__.py checks/batfish_common.py checks/batfish_helpers.py ./checks/

USER app

# Streamlit reads these variables. A deployment that needs another port, such as
# Styrmin's generic-app driver (8080), overrides STREAMLIT_SERVER_PORT.
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail "http://localhost:${STREAMLIT_SERVER_PORT}/_stcore/health" || exit 1

CMD ["streamlit", "run", "Home.py"]
