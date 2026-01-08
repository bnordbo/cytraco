#!/usr/bin/env bash
set -euo pipefail

# Generate org-mode statistics report for a PR
# Usage: pr-stats.sh <PR_NUMBER>

if [ $# -ne 1 ]; then
    echo "Usage: $0 <PR_NUMBER>" >&2
    exit 1
fi

PR_NUM="$1"

# Get PR info
PR_INFO=$(gh pr view "$PR_NUM" --json additions,deletions,changedFiles,commits,baseRefName,headRefName)
ADDITIONS=$(echo "$PR_INFO" | jq -r '.additions')
DELETIONS=$(echo "$PR_INFO" | jq -r '.deletions')
FILES_CHANGED=$(echo "$PR_INFO" | jq -r '.changedFiles')
BASE_BRANCH=$(echo "$PR_INFO" | jq -r '.baseRefName')
HEAD_BRANCH=$(echo "$PR_INFO" | jq -r '.headRefName')

# Get commit info
COMMITS=$(echo "$PR_INFO" | jq -r '.commits')
TOTAL_COMMITS=$(echo "$COMMITS" | jq 'length')
FIRST_COMMIT=$(echo "$COMMITS" | jq -r '.[0].oid[0:7]')
LAST_COMMIT=$(echo "$COMMITS" | jq -r '.[-1].oid[0:7]')

# Get first commit stats
FIRST_STATS=$(git show "$FIRST_COMMIT" --shortstat --format='')
FIRST_FILES=$(echo "$FIRST_STATS" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+')
FIRST_INSERTIONS=$(echo "$FIRST_STATS" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")

# Get changes from first to last commit
if [ "$TOTAL_COMMITS" -gt 1 ]; then
    ITERATION_STATS=$(git diff "$FIRST_COMMIT".."$LAST_COMMIT" --shortstat)
    ITER_FILES=$(echo "$ITERATION_STATS" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo "0")
    ITER_INSERTIONS=$(echo "$ITERATION_STATS" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
    ITER_DELETIONS=$(echo "$ITERATION_STATS" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo "0")
    ITER_NET=$((ITER_INSERTIONS - ITER_DELETIONS))
    REVIEW_COMMITS=$((TOTAL_COMMITS - 1))
else
    ITER_FILES=0
    ITER_INSERTIONS=0
    ITER_DELETIONS=0
    ITER_NET=0
    REVIEW_COMMITS=0
fi

# Get comment stats
COMMENTS=$(gh api "repos/{owner}/{repo}/pulls/$PR_NUM/comments")
TOTAL_COMMENTS=$(echo "$COMMENTS" | jq 'length')
ORIGINAL_COMMENTS=$(echo "$COMMENTS" | jq '[.[] | select(.in_reply_to_id == null)] | length')
REPLY_COMMENTS=$(echo "$COMMENTS" | jq '[.[] | select(.in_reply_to_id)] | length')

# Get file list from first commit
FILES_CREATED=$(git show "$FIRST_COMMIT" --name-only --format='' | sort)

# Generate org-mode output
cat <<EOF
** Code Changes

*** Final PR state
- Files changed :: $FILES_CHANGED
- Lines added :: +$ADDITIONS
- Lines removed :: -$DELETIONS
- Net change :: +$((ADDITIONS - DELETIONS)) lines

*** Initial implementation (first commit)
- Files created :: $FIRST_FILES
- Lines added :: +$FIRST_INSERTIONS (pure implementation)

*** Review iteration changes (commits 2-$TOTAL_COMMITS)
- Files modified :: $ITER_FILES
- Changes :: +$ITER_INSERTIONS, -$ITER_DELETIONS lines (net $ITER_NET lines)

** Development Process

*** Commits
- Total commits :: $TOTAL_COMMITS
  - Initial implementation :: 1
  - Refinement/review commits :: $REVIEW_COMMITS

*** Review Activity
- Original review comments :: $ORIGINAL_COMMENTS
- Response comments :: $REPLY_COMMENTS
- Total comment threads :: $TOTAL_COMMENTS

** Files Created

EOF

# List files by type
echo "*** Production code"
echo "$FILES_CREATED" | grep -v '^tests/' | while read -r file; do
    echo "- ~$file~"
done

echo ""
echo "*** Tests"
echo "$FILES_CREATED" | grep '^tests/' | while read -r file; do
    echo "- ~$file~"
done
