FROM alpine:3.24.2

ARG DUCKDB_VERSION=1.5.6

# curl fetches the inputs and uploads the output; DuckDB runs model.sql.
# The checksums are the release asset digests for DuckDB v1.5.6.
RUN apk add --no-cache curl libstdc++ \
    && case "$(apk --print-arch)" in \
        x86_64) arch=amd64 sha256=b146bc46094e67f713e0a83a0309910dfbc6696a557e651f484f2d2f80e54f6b ;; \
        aarch64) arch=arm64 sha256=693c977b4a6b97cb5dbb445fb68750bb1e931e4a2b5887d75c2147265e8ce063 ;; \
        *) echo "Unsupported architecture: $(apk --print-arch)" >&2; exit 1 ;; \
    esac \
    && curl -fsSL -o /tmp/duckdb.gz \
        "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/duckdb_cli-linux-${arch}-musl.gz" \
    && echo "${sha256}  /tmp/duckdb.gz" | sha256sum -c - \
    && gunzip -c /tmp/duckdb.gz > /usr/local/bin/duckdb \
    && chmod +x /usr/local/bin/duckdb \
    && rm /tmp/duckdb.gz

WORKDIR /app

COPY model.sql entrypoint.sh ./

CMD [ "/app/entrypoint.sh" ]
