#!/usr/bin/env bash
# Developer Hook Setup Script for IrrigAgent

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing IrrigAgent Git Pre-Commit Hooks...${NC}"

if [ ! -d ".git" ]; then
    echo -e "${RED}[✗] Error: .git directory not found. Please run this script from the repository root.${NC}"
    exit 1
fi

if [ ! -f "scripts/pre-commit.sh" ]; then
    echo -e "${RED}[✗] Error: scripts/pre-commit.sh not found.${NC}"
    exit 1
fi

mkdir -p .git/hooks

cp scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo -e "${GREEN}[✓] Pre-commit hook installed successfully at .git/hooks/pre-commit${NC}"
