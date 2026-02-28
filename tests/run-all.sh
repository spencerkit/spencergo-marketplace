#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source helpers
source "$SCRIPT_DIR/test-helpers.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

main() {
    print_header "spencergo Skills Test Suite"

    # Check prerequisites
    echo "Checking prerequisites..."

    if ! command -v claude &> /dev/null; then
        echo -e "${RED}Error: claude command not found${NC}"
        echo "Please install Claude Code first"
        exit 1
    fi
    echo "  ✓ Claude CLI found"

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 not found${NC}"
        exit 1
    fi
    echo "  ✓ Python3 found"

    # Run skill triggering tests
    echo ""
    echo "Running skill triggering tests..."
    echo ""

    cd "$SCRIPT_DIR/skill-triggering"
    chmod +x run-all.sh
    ./run-all.sh

    print_header "All Tests Complete"
    echo "See results above for details"
}

main "$@"
