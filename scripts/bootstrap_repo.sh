#!/usr/bin/env bash
set -euo pipefail

# Run only after an empty private GitHub repository named Backscatter exists.
# Requires git and authenticated GitHub access.

REPO_URL="${1:-git@github.com:Phloraxx/Backscatter.git}"

git init
git add .
git commit -m "chore: initialize Backscatter project context"
git branch -M main
git remote add origin "$REPO_URL"
git push -u origin main
