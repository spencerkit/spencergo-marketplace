#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CASES_DIR="$SCRIPT_DIR/cases"

# Source helpers
source "$PROJECT_ROOT/tests/test-helpers.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

run_test_case() {
    local skill="$1"
    local test_name="$2"
    local prompt="$3"
    local expected_contains="$4"
    local not_expected="$5"
    local timeout="${6:-60}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "\n${BLUE}[$test_name]${NC}"
    echo "Prompt: $prompt"

    # Create temp project
    local test_dir=$(mktemp -d)

    # Run Claude
    cd "$test_dir"
    local output_file="/tmp/skill-test-$skill-$test_name.out"

    if timeout "$timeout" claude -p "$prompt" \
        --permission-mode bypassPermissions \
        --add-dir "$test_dir" \
        --dangerously-skip-permissions \
        > "$output_file" 2>&1; then

        # Find session file
        local session_file=$(find_session_file "$test_dir")

        if [ -z "$session_file" ]; then
            echo -e "${YELLOW}[SKIP]${NC} Could not find session file"
            SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
            rm -rf "$test_dir"
            return
        fi

        # Check expected contains
        local all_passed=true

        if [ -n "$expected_contains" ]; then
            for expected in $(echo "$expected_contains" | tr ',' ' '); do
                if ! grep -qi "$expected" "$session_file"; then
                    echo -e "${RED}  Missing expected: $expected${NC}"
                    all_passed=false
                fi
            done
        fi

        # Check not expected
        if [ -n "$not_expected" ]; then
            for unexpected in $(echo "$not_expected" | tr ',' ' '); do
                if grep -qi "$unexpected" "$session_file"; then
                    echo -e "${RED}  Found unexpected: $unexpected${NC}"
                    all_passed=false
                fi
            done
        fi

        if [ "$all_passed" = true ]; then
            echo -e "${GREEN}[PASS]${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}[FAIL]${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo -e "${RED}[FAIL]${NC} Test timed out or failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Cleanup
    rm -rf "$test_dir"
    rm -f "$output_file"
}

# Parse test cases from JSON
run_skill_tests() {
    local skill_file="$1"
    local skill_name=$(basename "$skill_file" .json)

    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}Testing: $skill_name${NC}"
    echo -e "${YELLOW}========================================${NC}"

    # Use Node.js to parse JSON
    local test_cases=$(node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$skill_file', 'utf-8'));
for (const tc of data.test_cases || []) {
  console.log((tc.name || '') + '||' +
    (tc.prompt || '') + '||' +
    ((tc.expected_contains || []).join(',')) + '||' +
    ((tc.not_expected || []).join(',')) + '||' +
    (tc.timeout || 60));
}
" 2>/dev/null || true)

    if [ -z "$test_cases" ]; then
        echo "No test cases found"
        return
    fi

    while IFS='||' read -r test_name prompt expected not_expected timeout; do
        if [ -n "$test_name" ]; then
            run_test_case "$skill_name" "$test_name" "$prompt" "$expected" "$not_expected" "$timeout"
        fi
    done <<< "$test_cases"
}

main() {
    print_header "Skill Triggering Tests"

    # Check if Claude is available
    if ! command -v claude &> /dev/null; then
        echo -e "${RED}Error: claude command not found${NC}"
        exit 1
    fi

    # Run tests for each skill case file
    for case_file in "$CASES_DIR"/*.json; do
        if [ -f "$case_file" ]; then
            run_skill_tests "$case_file"
        fi
    done

    # Print summary
    print_header "Test Summary"
    echo "Total:  $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
    echo -e "Skipped: ${YELLOW}$SKIPPED_TESTS${NC}"

    if [ $FAILED_TESTS -gt 0 ]; then
        exit 1
    fi
}

main "$@"
