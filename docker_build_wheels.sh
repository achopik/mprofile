#!/bin/bash
set -exuo pipefail

PLATFORMS="x86_64"

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--platform)
            PLATFORMS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

python -m build --sdist

SRC_DIR="$(pwd)"

build_x86_64() {
    docker run -i --rm \
        -v "$SRC_DIR:/src" \
        -e PLAT=manylinux2014_x86_64 \
        quay.io/pypa/manylinux2014_x86_64 \
        /src/build_wheels.sh
}

build_arm64() {
    docker run --platform=linux/arm64 -i --rm \
        -v "$SRC_DIR:/src" \
        -e PLAT=manylinux2014_aarch64 \
        quay.io/pypa/manylinux2014_aarch64 \
        /src/build_wheels.sh
}

case "$PLATFORMS" in
    x86_64)
        build_x86_64
        ;;
    arm64)
        build_arm64
        ;;
    *)
        echo "Unknown platform: $PLATFORMS"
        exit 1
        ;;
esac