#!/usr/bin/env bash
# Test helpers for spencergo skills testing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results directory
TEST_RESULTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/test-results"

# Plugin directory (local skills)
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.claude-plugin"

# Create test-results directory if not exists
mkdir -p "$TEST_RESULTS_DIR"

# Create a temporary test project
create_test_project() {
    local test_name="${1:-test}"
    local timestamp=$(date +%s)
    local test_dir="$TEST_RESULTS_DIR/${test_name}-${timestamp}"
    mkdir -p "$test_dir"
    echo "$test_dir"
}

# Cleanup test project
cleanup_test_project() {
    local test_dir="$1"
    if [ -d "$test_dir" ]; then
        rm -rf "$test_dir"
    fi
}

# Run Claude with a skill prompt
run_claude_skill() {
    local skill="$1"
    local prompt="$2"
    local test_dir="$3"
    local timeout="${4:-300}"

    cd "$test_dir"

    timeout "$timeout" claude -p "$prompt" \
        --permission-mode bypassPermissions \
        --add-dir "$test_dir" \
        --dangerously-skip-permissions \
        2>&1
}

# Find the most recent session file for a project
find_session_file() {
    local project_dir="$1"
    # Claude encodes path by replacing / with -
    local project_escaped=$(echo "$project_dir" | sed 's/\//-/g' | sed 's/^-//')
    local session_dir="$HOME/.claude/projects/$project_escaped"

    if [ -d "$session_dir" ]; then
        find "$session_dir" -name "*.jsonl" -type f -mmin -60 2>/dev/null | sort -r | head -1
    fi
}

# Copy session file to test-results for analysis
save_session() {
    local session_file="$1"
    local dest_dir="$2"

    if [ -f "$session_file" ]; then
        local basename=$(basename "$session_file")
        cp "$session_file" "$dest_dir/$basename"
        echo "$dest_dir/$basename"
    fi
}

# Check if session contains expected text
check_session_contains() {
    local session_file="$1"
    local expected="$2"

    if grep -q "$expected" "$session_file"; then
        return 0
    else
        return 1
    fi
}

# Check if session does NOT contain unexpected text
check_session_not_contains() {
    local session_file="$1"
    local unexpected="$2"

    if grep -q "$unexpected" "$session_file"; then
        return 1
    else
        return 0
    fi
}

# Check if skill was invoked in session
check_skill_invoked() {
    local session_file="$1"
    local skill_name="$2"

    if grep -q "\"skill\":\"$skill_name\"" "$session_file"; then
        return 0
    else
        return 1
    fi
}

# Print test result
print_result() {
    local test_name="$1"
    local result="$2"
    local message="${3:-}"

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}[PASS]${NC} $test_name"
    elif [ "$result" = "FAIL" ]; then
        echo -e "${RED}[FAIL]${NC} $test_name"
        if [ -n "$message" ]; then
            echo -e "       $message"
        fi
    elif [ "$result" = "SKIP" ]; then
        echo -e "${YELLOW}[SKIP]${NC} $test_name"
    fi
}

# Print section header
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Load test case from JSON
load_test_case() {
    local json_file="$1"
    local test_name="$2"

    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$json_file', 'utf-8'));
const test = data.test_cases?.find(t => t.name === '$test_name');
if (test) console.log(JSON.stringify(test));
"
}

export -f create_test_project
export -f cleanup_test_project
export -f run_claude_skill
export -f find_session_file
export -f save_session
export -f check_session_contains
export -f check_session_not_contains
export -f check_skill_invoked
export -f print_result
export -f print_header
export -f load_test_case
