# Use an official Python runtime as a parent image
FROM python:3.8-alpine

# Install applications
RUN apk add --no-cache \
        ca-certificates \
        gcc \
        curl \
        git \
        nodejs \
        npm \
        musl-dev \
        bash

# Rust install locations and the version to be downloaded
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH \
    RUST_VERSION=1.70

# Get rustup-init (initialized the download). Download the specified version of Rust, cargo (pkg manager) and rustup (update manager)
RUN set -eux; \
    apkArch="$(apk --print-arch)"; \
    case "$apkArch" in \
        x86_64) rustArch='x86_64-unknown-linux-musl'; rustupSha256='241a99ff02accd2e8e0ef3a46aaa59f8d6934b1bb6e4fba158e1806ae028eb25' ;; \
        aarch64) rustArch='aarch64-unknown-linux-musl'; rustupSha256='6a2691ced61ef616ca196bab4b6ba7b0fc5a092923955106a0c8e0afa31dbce4' ;; \
        *) echo >&2 "unsupported architecture: $apkArch"; exit 1 ;; \
    esac; \
    url="https://static.rust-lang.org/rustup/archive/1.25.2/${rustArch}/rustup-init"; \
    wget "$url"; \
    echo "${rustupSha256} *rustup-init" | sha256sum -c -; \
    chmod +x rustup-init; \
    ./rustup-init -y --no-modify-path --profile minimal --default-toolchain $RUST_VERSION --default-host ${rustArch}; \
    rm rustup-init; \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME; \
    rustup --version; \
    cargo --version; \
    rustc --version;

# Install gulp-cli for everyone (-g) 
RUN npm i -g gulp-cli

# Using cargo, install mdbook and mermaid
RUN cargo --color=never install mdbook mdbook-mermaid

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependencies file and local 'src' directory to the working directory
COPY requirements.txt src/ ./

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Git
RUN apk add --no-cache git openssh

# Run the application
CMD [ "python", "./updater.py" ]