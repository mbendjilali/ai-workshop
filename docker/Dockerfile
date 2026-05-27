# alteia-grid-synth lab image
#
# Strategy: extend gridappsd/cimhub:1.1.0 (ADR-002, G-4) — inherits OpenDSS, GridLAB-D,
# Java 11, and CIMHub JAR layout; add Python 3.10+ and editable project install.
#
# Build: docker build -f docker/Dockerfile -t alteia-grid-synth:lab .

ARG CIMHUB_IMAGE=gridappsd/cimhub:1.1.0
ARG PYTHON_IMAGE=python:3.10-bookworm

FROM ${CIMHUB_IMAGE} AS cimhub-tools

FROM ${PYTHON_IMAGE}

ARG CIMHUB_IMAGE
ARG CIMHUB_RELEASE=2024.06.0

LABEL org.opencontainers.image.title="alteia-grid-synth-lab"
LABEL org.opencontainers.image.description="CDPSM hub pipeline lab image with OpenDSS, CIMHub, GridLAB-D"
LABEL org.opencontainers.image.source="https://github.com/alteia/alteia-grid-synth"
LABEL alteia.cimhub.base="${CIMHUB_IMAGE}"
LABEL alteia.cimhub.release="${CIMHUB_RELEASE}"

ENV DEBIAN_FRONTEND=noninteractive \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    CIMHUB_HOME=/opt/cimhub \
    PATH="/usr/lib/jvm/java-11-openjdk-amd64/bin:/usr/local/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Java 11 JRE — copied from CIMHub base (bullseye); openjdk-11 is not in bookworm repos
COPY --from=cimhub-tools /usr/lib/jvm/java-11-openjdk-amd64 /usr/lib/jvm/java-11-openjdk-amd64
COPY --from=cimhub-tools /etc/java-11-openjdk /etc/java-11-openjdk
COPY --from=cimhub-tools /etc/ssl/certs/java /etc/ssl/certs/java

# GridLAB-D (G-4) — copied from CIMHub reference image
COPY --from=cimhub-tools /usr/local/bin/gridlabd /usr/local/bin/gridlabd
COPY --from=cimhub-tools /usr/local/bin/gridlabd.sh /usr/local/bin/gridlabd.sh
COPY --from=cimhub-tools /usr/local/lib/ /usr/local/lib/
COPY --from=cimhub-tools /usr/local/share/tzinfo.txt /usr/local/share/tzinfo.txt
COPY --from=cimhub-tools /usr/local/share/unitfile.txt /usr/local/share/unitfile.txt

# OpenDSS command-line driver
COPY --from=cimhub-tools /usr/local/bin/opendsscmd /usr/local/bin/opendsscmd

# CIMHub JAR releases and support files
COPY --from=cimhub-tools /app/releases ${CIMHUB_HOME}/releases
COPY --from=cimhub-tools /app/queries/cimhubconfig.json ${CIMHUB_HOME}/queries/cimhubconfig.json

RUN ldconfig \
    && chmod +x /usr/local/bin/gridlabd /usr/local/bin/gridlabd.sh /usr/local/bin/opendsscmd

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .

# Default shell for interactive lab use; pipeline stages invoke grid-synth directly.
CMD ["/bin/bash"]
