# Usage

## Setup

Replace UID (`1000`) and GID (`1000`) in `Dockerfile` with yours.

## With Docker

To build image:

    docker build -t sdindex-dev .

To start shell:

    docker run -it --rm -v $PWD/../..:/sdindex -w /sdindex sdindex-dev bash

## With Docker Compose

To start shell:

    docker compose run --rm ws bash
