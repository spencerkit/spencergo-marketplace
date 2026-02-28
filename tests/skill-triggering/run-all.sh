#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CASES_DIR="$SCRIPT_DIR/cases"
PLUGIN_DIR="$PROJECT_ROOT/.claude-plugin"

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

    # Create test project in test-results directory
    local test_dir=$(create_test_project "${skill}-${test_name}")
    local output_file="$test_dir/output.txt"

    # Run Claude with local plugin
    cd "$test_dir"

    if timeout "$timeout" claude -p "$prompt" \
        --permission-mode bypassPermissions \
        --add-dir "$test_dir" \
        --plugin-dir "$PLUGIN_DIR" \
        --dangerously-skip-permissions \
        > "$output_file" 2>&1; then

        # Find session file
        local session_file=$(find_session_file "$test_dir")

        if [ -z "$session_file" ]; then
            echo -e "${YELLOW}[SKIP]${NC} Could not find session file"
            SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
            cleanup_test_project "$test_dir"
            return
        fi

        # Copy session to test-results for analysis
        save_session "$session_file" "$test_dir"

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
            echo "  Session saved: $test_dir"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}[FAIL]${NC}"
            echo "  Session saved: $test_dir"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo -e "${RED}[FAIL]${NC} Test timed out or failed"
        echo "  Output saved: $test_dir"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Keep test results for analysis
    echo "  Results: $test_dir"
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
