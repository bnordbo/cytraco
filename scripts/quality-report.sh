#!/usr/bin/env bash
set -euo pipefail

# Generate org-mode quality metrics report
# Usage: quality-report.sh [path]
# If path provided, analyzes specific directory/file; otherwise analyzes entire project

TARGET="${1:-.}"

echo "** Code Quality Report"
echo ""
echo "*** Target"
echo "- Path :: ~${TARGET}~"
echo "- Generated :: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Test Coverage
echo "*** Test Coverage"
if command -v coverage &> /dev/null; then
    coverage run -m pytest --quiet 2>/dev/null || true
    COVERAGE_REPORT=$(coverage report 2>/dev/null | tail -2)
    COVERAGE_PCT=$(echo "$COVERAGE_REPORT" | tail -1 | awk '{print $NF}')
    COVERAGE_STMTS=$(echo "$COVERAGE_REPORT" | tail -1 | awk '{print $2}')
    COVERAGE_MISS=$(echo "$COVERAGE_REPORT" | tail -1 | awk '{print $3}')
    echo "- Coverage :: $COVERAGE_PCT ($COVERAGE_STMTS statements, $COVERAGE_MISS missed)"
else
    echo "- Coverage :: Not available (install coverage)"
fi
echo ""

# Linter
echo "*** Linter (Ruff)"
if command -v ruff &> /dev/null; then
    RUFF_OUTPUT=$(ruff check "$TARGET" 2>&1 || true)
    if echo "$RUFF_OUTPUT" | grep -q "All checks passed"; then
        echo "- Status :: ✓ All checks passed"
    else
        ERROR_COUNT=$(echo "$RUFF_OUTPUT" | grep -oE 'Found [0-9]+ error' | grep -oE '[0-9]+' || echo "0")
        echo "- Status :: ✗ $ERROR_COUNT errors found"
        echo "- Details :: Run ~ruff check $TARGET~ for specifics"
    fi
else
    echo "- Status :: Not available (install ruff)"
fi
echo ""

# Dead Code
echo "*** Dead Code Detection (Vulture)"
if command -v vulture &> /dev/null; then
    VULTURE_OUTPUT=$(vulture 2>&1 || true)
    if [ -z "$VULTURE_OUTPUT" ]; then
        echo "- Status :: ✓ No dead code found"
    else
        DEAD_COUNT=$(echo "$VULTURE_OUTPUT" | wc -l | tr -d ' ')
        echo "- Status :: ✗ $DEAD_COUNT potential dead code items"
        echo "- Details :: Run ~vulture~ for specifics"
    fi
else
    echo "- Status :: Not available (install vulture)"
fi
echo ""

# Cyclomatic Complexity
echo "*** Cyclomatic Complexity (Radon)"
if command -v radon &> /dev/null; then
    # Get average complexity and count functions with CC > threshold
    CC_OUTPUT=$(radon cc "$TARGET" -a -s 2>/dev/null || echo "")
    if [ -n "$CC_OUTPUT" ]; then
        AVG_CC=$(echo "$CC_OUTPUT" | grep "Average complexity:" | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "N/A")
        HIGH_CC=$(radon cc "$TARGET" -n 10 2>/dev/null | grep -E '^\s+[A-Z]' | wc -l | tr -d ' ')
        echo "- Average complexity :: $AVG_CC"
        echo "- Functions with CC > 10 :: $HIGH_CC"
    else
        echo "- Status :: No functions analyzed"
    fi
else
    echo "- Status :: Not available (install radon)"
fi
echo ""

# Maintainability Index
echo "*** Maintainability Index (Radon)"
if command -v radon &> /dev/null; then
    MI_OUTPUT=$(radon mi "$TARGET" -s 2>/dev/null || echo "")
    if [ -n "$MI_OUTPUT" ]; then
        AVG_MI=$(echo "$MI_OUTPUT" | tail -1 | grep -oE '[0-9]+\.[0-9]+' || echo "N/A")
        echo "- Average MI :: $AVG_MI (0-100, higher is better)"
        # Count files by rank
        RANK_A=$(echo "$MI_OUTPUT" | grep -c " - A " || echo "0")
        RANK_B=$(echo "$MI_OUTPUT" | grep -c " - B " || echo "0")
        RANK_C=$(echo "$MI_OUTPUT" | grep -c " - C " || echo "0")
        echo "- Rank distribution :: A: $RANK_A, B: $RANK_B, C: $RANK_C"
    else
        echo "- Status :: No files analyzed"
    fi
else
    echo "- Status :: Not available (install radon)"
fi
echo ""

# Documentation Coverage
echo "*** Documentation Coverage (Interrogate)"
if command -v interrogate &> /dev/null; then
    INTERROGATE_OUTPUT=$(interrogate "$TARGET" 2>/dev/null || true)
    DOC_PCT=$(echo "$INTERROGATE_OUTPUT" | grep "TOTAL" | awk '{print $NF}')
    if [ -n "$DOC_PCT" ]; then
        echo "- Documentation coverage :: $DOC_PCT"
    else
        echo "- Status :: Unable to calculate"
    fi
else
    echo "- Status :: Not available (install interrogate)"
fi
echo ""

# Type Coverage
echo "*** Type Coverage (Mypy)"
if command -v mypy &> /dev/null; then
    MYPY_OUTPUT=$(mypy "$TARGET" 2>&1 || true)
    if echo "$MYPY_OUTPUT" | grep -q "Success"; then
        echo "- Status :: ✓ No type errors"
    else
        ERROR_COUNT=$(echo "$MYPY_OUTPUT" | grep -oE 'Found [0-9]+ error' | grep -oE '[0-9]+' || echo "0")
        if [ "$ERROR_COUNT" = "0" ]; then
            echo "- Status :: ✓ No type errors"
        else
            echo "- Status :: ✗ $ERROR_COUNT type errors found"
            echo "- Details :: Run ~mypy $TARGET~ for specifics"
        fi
    fi
else
    echo "- Status :: Not available (install mypy)"
fi
echo ""

# Test/Code Ratio
echo "*** Test/Code Ratio"
PROD_LINES=$(find cytraco -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
TEST_LINES=$(find tests -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
if [ "$PROD_LINES" -gt 0 ]; then
    RATIO=$(echo "scale=2; $TEST_LINES / $PROD_LINES" | bc)
    echo "- Production code :: $PROD_LINES lines"
    echo "- Test code :: $TEST_LINES lines"
    echo "- Ratio :: ${RATIO}:1 (test:production)"
    if (( $(echo "$RATIO >= 1.0" | bc -l) )); then
        echo "- Assessment :: ✓ Healthy (≥1.0)"
    else
        echo "- Assessment :: Low test coverage by volume"
    fi
else
    echo "- Status :: Unable to calculate"
fi
echo ""

# Summary
echo "** Summary"
echo ""
echo "Run individual tools for detailed reports:"
echo "- ~pytest -v~"
echo "- ~coverage report~"
echo "- ~ruff check .~"
echo "- ~vulture~"
echo "- ~radon cc cytraco -a~"
echo "- ~radon mi cytraco -s~"
echo "- ~interrogate cytraco~"
echo "- ~mypy cytraco~"
