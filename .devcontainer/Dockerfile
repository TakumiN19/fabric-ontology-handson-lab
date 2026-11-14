# Digest pinned from mcr.microsoft.com/devcontainers/python:1-3.12-bookworm.
FROM mcr.microsoft.com/devcontainers/python@sha256:7876580dc67fd460fd962f004cbeb480027e9bbc0657096f1087db11f9eaff39

# Remove stale Yarn apt source before Dev Container features run apt update.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources
