FROM python@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534
LABEL org.argo.purpose="stage0-scienceagentbench-certification"
LABEL org.argo.requirements.sha256="a8feaf196a902c3a8fcaf8f0e7883450c9c0a3e6a862695e19eca305bea3de0c"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends libxrender1 libexpat1 libxext6 && rm -rf /var/lib/apt/lists/*
COPY requirements.lock /tmp/requirements.lock
RUN python -m pip install --only-binary=:all: --require-hashes -r /tmp/requirements.lock
COPY import_probe.py /opt/argo/import_probe.py
ENTRYPOINT ["python"]
