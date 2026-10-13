FROM debian:12.15-slim

ENV LANG=C.UTF-8

# Debian ships R and the forecast, httr and jsonlite packages prebuilt, so
# nothing compiles. The cleanup removes documentation, translations and
# package help and tests, which a model run never reads.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        r-base-core r-cran-forecast r-cran-httr r-cran-jsonlite \
    && rm -rf /var/lib/apt/lists/* \
        /usr/share/doc /usr/share/man /usr/share/info /usr/share/locale \
        /usr/share/R/doc /usr/lib/R/library/translations \
    && find /usr/lib/R/library /usr/lib/R/site-library -mindepth 2 -maxdepth 2 \
        -type d \( -name help -o -name html -o -name doc -o -name tests -o -name po \) \
        -exec rm -rf {} +

WORKDIR /app

COPY model/ model/

CMD [ "Rscript", "model/main.R" ]
