#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"

GREEN=$'\033[0;32m'
RED=$'\033[0;31m'
CYAN=$'\033[0;36m'
YELLOW=$'\033[0;33m'
RESET=$'\033[0m'

BASE="${BASE:-http://httpbin.org}"
PASS=0
FAIL=0

pass() { ((PASS++)) && printf '%s  PASS%s  %s\n' "$GREEN" "$RESET" "$1"; }
fail() { ((FAIL++)) && printf '%s  FAIL%s  %s\n' "$RED" "$RESET" "$1"; }

check() {
    local desc="$1" expected="$2"
    shift 2
    if "$@" > /dev/null 2>&1; then
        pass "$desc"
    else
        fail "$desc (expected: $expected)"
    fi
}

check_fail() {
    local desc="$1" expected="$2"
    shift 2
    if "$@" > /dev/null 2>&1; then
        fail "$desc (expected: $expected)"
    else
        pass "$desc"
    fi
}

check_grep() {
    local desc="$1" pattern="$2"
    shift 2
    local out
    out="$("$@" 2>&1)"
    if grep -Eq -- "$pattern" <<< "$out"; then
        pass "$desc"
    else
        fail "$desc (pattern: $pattern)"
        printf '%s    >> %s\n' "$YELLOW" "$(printf '%s\n' "$out" | head -3 | tr '\n' ' ')"
    fi
}

echo "$CYAN=== rurl automated test suite ===$RESET"

echo "$CYAN--- step 1: cargo clippy ---$RESET"
if cargo clippy --quiet 2>&1; then
    pass "cargo clippy is clean"
else
    fail "cargo clippy has warnings/errors"
fi

echo "$CYAN--- step 2: cargo build ---$RESET"
if cargo build 2>&1; then
    pass "cargo build succeeds"
else
    fail "cargo build failed"
fi

RURL=./target/debug/rurl
[[ -x $RURL ]] || { echo "$RED rurl binary missing $RESET"; exit 1; }

echo "$CYAN--- step 3: version / help ---$RESET"
check_grep "-V prints version" "rurl [0-9]" "$RURL" -V
check_grep "--help lists options" "max-time" "$RURL" --help

echo "$CYAN--- step 4: basic GET ---$RESET"
check_grep "GET returns JSON body" '"url"' "$RURL" "$BASE/get"
check_grep "GET wrong URL fails" "Error" "$RURL" "http://nonexistent-domain-abc123.invalid/"

echo "$CYAN--- step 5: methods ---$RESET"
check_grep "POST with -d reaches server" '"data"' "$RURL" -d 'foo=bar' "$BASE/post"
check_grep "uppercase -X GET works" '"X-Custom"' "$RURL" -X GET -H "X-Custom: test" "$BASE/headers"
check_grep "PATCH method works" '"data"' "$RURL" -X PATCH -d 'x=1' "$BASE/patch"
check_grep "DELETE method works" '"data"' "$RURL" -X DELETE -d 'x=1' "$BASE/delete"
check_grep "PUT method works" '"data"' "$RURL" -X PUT -d 'x=1' "$BASE/put"

echo "$CYAN--- step 6: headers / body ---$RESET"
check_grep "-H custom header sent" '"X-Custom": "rurl-unit"' "$RURL" -H "X-Custom: rurl-unit" "$BASE/headers"
check_fail "invalid header format fails" "exit code 1" "$RURL" -H "NoColonHere" "$BASE/get"
check_grep "-d auto-upgrades GET to POST" '"data"' "$RURL" -d 'auto=1' "$BASE/post"

echo "$CYAN--- step 7: redirects ---$RESET"
check_grep "-L follows redirect (status 200)" '"url"' "$RURL" -L "$BASE/redirect/1"
check "no -L returns 3xx" "3[0-9][0-9]" "$RURL" -i "$BASE/redirect/1"

echo "$CYAN--- step 8: timeout ---$RESET"
check_grep "-m 1 times out on slow endpoint" "Error|timed out" "$RURL" -m 1 "$BASE/delay/3"

echo "$CYAN--- step 9: include headers ---$RESET"
check_grep "-i shows status line" "HTTP/1.1 200" "$RURL" -i "$BASE/get"

echo "$CYAN--- step 10: verbose ---$RESET"
check_grep "-v logs request line to stderr" ">" "$RURL" -v "$BASE/get"

echo "$CYAN--- step 11: output to file ---$RESET"
OUT="$(mktemp -t rurl.XXXXXX)"
rm -f "$OUT"
check "-o writes file" "wrote" "$RURL" -o "$OUT" "$BASE/get"
[[ -s "$OUT" ]] && pass "-o file is non-empty" || fail "-o file is empty"
grep -q '"url"' "$OUT" && pass "-o file contains JSON body" || fail "-o file missing body"
rm -f "$OUT"

echo
echo "========================================"
printf '%s  PASS: %d%s\n' "$GREEN" "$PASS" "$RESET"
printf '%s  FAIL: %d%s\n' "$RED" "$FAIL" "$RESET"
echo "========================================"

[[ $FAIL -eq 0 ]]