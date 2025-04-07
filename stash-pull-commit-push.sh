#!/bin/bash

# 检查是否提供了提交信息
if [ -z "$1" ]; then
  echo "请提供提交信息"
  echo "用法: ./stash-pull-commit-push.sh '提交信息'"
  exit 1
fi

COMMIT_MSG="$1"

echo "1. 暂存当前修改..."
git stash save "暂存修改 $(date '+%Y-%m-%d %H:%M:%S')"

echo "2. 拉取远程最新代码..."
git pull

echo "3. 恢复暂存的修改..."
git stash pop

echo "4. 添加修改到暂存区..."
git add .

echo "5. 提交修改..."
git commit -m "$COMMIT_MSG"

echo "6. 推送到远程仓库..."
git push

echo "完成!"