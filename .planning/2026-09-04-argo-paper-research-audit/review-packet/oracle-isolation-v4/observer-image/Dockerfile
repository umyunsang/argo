FROM argo-sab-stage0@sha256:026ce848fa7de5d15510192aaeaadfe05cc252364df51ddc292d3655f0cc2060
LABEL org.argo.purpose="stage0-oracle-access-syscall-observer"
LABEL org.argo.observed-image.digest="sha256:026ce848fa7de5d15510192aaeaadfe05cc252364df51ddc292d3655f0cc2060"
RUN apt-get update && apt-get install -y --no-install-recommends strace && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["strace"]
