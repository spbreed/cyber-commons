#!/usr/bin/env bash
# Install the local git hooks. One hook, one job: no credential ever reaches a
# commit. Run once after cloning:
#
#   ./scripts/install-hooks.sh
#
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
hook="$root/.git/hooks/pre-commit"

cat > "$hook" <<'EOF'
#!/usr/bin/env bash
# Cyber Commons pre-commit: block credentials.
exec python3 "$(git rev-parse --show-toplevel)/scripts/check_secrets.py"
EOF
chmod +x "$hook"
echo "installed $hook"
python3 "$root/scripts/check_secrets.py"
