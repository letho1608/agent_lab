#!/bin/bash
# -*- coding: UTF8 -*-

python3 -m pip install pyoxidizer

# so let's copy important files necessary for the build
cp -r ../../pupy/agent lib/pupy/
cp -r ../../pupy/network lib/pupy/
cp -r ../../pupy/library_patches_py3 .

# Build native: pyoxidizer (đã cài ở trên)
pyoxidizer build --release

strip -s build/x86_64-unknown-linux-gnu/release/install/pyoxydizer_pupy
echo "saving built template to ~/.pupy/payload_templates/ ..."
mkdir -p ~/.pupy/payload_templates
cp ./build/x86_64-unknown-linux-gnu/release/install/pyoxydizer_pupy ~/.pupy/payload_templates/pupyx64-310.pyoxidizer.lin


# Windows: cần môi trường PyOxidizer (MSVC) rồi chạy pyoxidizer build --release
