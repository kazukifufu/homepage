#!/bin/bash

# 対象ディレクトリ（引数がない場合はカレントディレクトリ）
TARGET_DIR=${1:-.}

echo "Checking Python files in: $TARGET_DIR"

# flake8の実行
echo "--- Running flake8 ---"
find "$TARGET_DIR" -name "*.py" -print0 | xargs -0 flake8

# pylintの実行
echo "--- Running pylint ---"
find "$TARGET_DIR" -name "*.py" -print0 | xargs -0 pylint

echo "Done."
