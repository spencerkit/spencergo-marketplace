#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILLS_DIR="$PROJECT_ROOT/skills"
TEST_RESULTS_DIR="$PROJECT_ROOT/tests/test-results"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$TEST_RESULTS_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}spencergo Skills Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"

echo "Checking prerequisites..."

if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: claude command not found${NC}"
    exit 1
fi
echo "  ✓ Claude CLI found"

if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: node not found${NC}"
    exit 1
fi
echo "  ✓ Node.js found"

echo ""
echo "Running universal skill tests..."
echo ""

# Run Node.js test runner with skills directory
node "$SCRIPT_DIR/universal-test-runner.js" "$SKILLS_DIR"
