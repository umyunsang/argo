FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1
COPY requirements.lock /opt/house-price/requirements.lock
RUN python -m pip install --disable-pip-version-check --no-cache-dir --only-binary=:all: --require-hashes -r /opt/house-price/requirements.lock \
    && python -m pip check
WORKDIR /work
USER 65532:65532
CMD ["python", "--version"]
