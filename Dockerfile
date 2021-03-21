FROM golang:1.16.2-buster as build
RUN mkdir /app
COPY . /app
RUN cd /app; ./build.sh

FROM debian:10.8-slim as ponylib
LABEL org.opencontainers.image.title="Ponylib v2"
LABEL org.opencontainers.image.description="Fb2 library with CLI & web UI"
LABEL org.opencontainers.image.authors="Nikita Kovalev <https://github.com/maizy>"
LABEL org.opencontainers.image.url="https://github.com/maizy/PonyLib"
LABEL org.opencontainers.image.licenses="Apache-2.0"
RUN mkdir /app
WORKDIR /app
COPY --from=build /app/bin/ponylib /app/ponylib
ENTRYPOINT ["/app/ponylib"]
