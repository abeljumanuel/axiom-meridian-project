#!/usr/bin/env bash
# PreToolUse hook (Bash). Registered in settings.json with "if" filters for
# `git tag*`, `uv publish*` and `twine upload*`.
#
# 1. Blocks publishing to PyPI from this machine: CI (release.yml) publishes
#    when a vX.Y.Z tag is pushed.
# 2. Blocks creating a release tag vX.Y.Z unless the working tree is clean and
#    `scripts/release_version.py check X.Y.Z --require-changelog` passes
#    (__init__.py, server.json, marketplace.json, plugin.json and CHANGELOG.md
#    all agree on the version).
# Listing, deleting and verifying tags is always allowed.

input=$(cat)
command=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

deny() {
  jq -n --arg reason "$1" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
  exit 0
}

case "$command" in
  *"uv publish"*|*"twine upload"*)
    deny "Releases are published to PyPI by CI (.github/workflows/release.yml) when a vX.Y.Z tag is pushed. Do not publish from this machine; follow the release-version skill. If the user really wants a manual publish, they must run it themselves."
    ;;
esac

case "$command" in
  *"git tag"*) ;;
  *) exit 0 ;;
esac

args=${command#*git tag}
for flag in -l --list -d --delete -v --verify; do
  case " $args " in
    *" $flag "*) exit 0 ;;
  esac
done

tag=$(printf '%s\n' "$args" | tr ' ' '\n' | sed "s/[\"']//g" \
  | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+((a|b|rc)[0-9]+)?$' | head -n 1)
[ -z "$tag" ] && exit 0
version=${tag#v}

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0

problems=""
if [ -n "$(git -C "$root" status --porcelain 2>/dev/null)" ]; then
  problems="- the working tree has uncommitted or untracked changes (commit the release first)"$'\n'
fi

if command -v python3 >/dev/null 2>&1; then
  py=(python3)
elif command -v uv >/dev/null 2>&1; then
  py=(uv run --no-project python)
else
  deny "Cannot verify release tag $tag: neither python3 nor uv is available to run scripts/release_version.py."
fi

check_output=$(cd "$root" && "${py[@]}" scripts/release_version.py check "$version" --require-changelog 2>&1)
if [ $? -ne 0 ]; then
  problems+=$(printf '%s\n' "$check_output" | grep '^  - ' | sed 's/^  //')$'\n'
fi

if [ -n "$problems" ]; then
  deny "Refusing to create release tag $tag:"$'\n'"${problems}Fix these (see the release-version skill; \`python3 scripts/release_version.py bump $version\` updates every version declaration) and try again."
fi

exit 0
