# Deferred Work

## Deferred from: code review of 1-1-initialize-pipeline-repo-and-docker-lab-image (2026-05-27)

- CIMHub JAR presence not in verify-lab-image.sh — add `ls /opt/cimhub/releases` in a later hardening pass
- Dockerfile amd64-only Java path — multi-arch out of scope for Story 1.1
- start-blazegraph.sh vs compose use different container names — document cleanup when switching paths

## Deferred from: code review of 1-3-implement-export-cim100-pipeline-stage (2026-05-27)

- ~~Docker root-owned `work/`~~ **Resolved 2026-05-27:** `-u $(id -u):$(id -g)` in `export_cim100.py`, `verify-ieee13-mrid-stability.sh`, `scripts/lib/docker.sh`
