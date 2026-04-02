#!/usr/bin/env bash
# boot.sh — openclaw environment bootstrap
# Modes: install (default) | --update | --repair | --check | --help

set -euo pipefail

# ── Privilege escalation ──────────────────────────────────────────────────────
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    _SUDOERS_CHECK="/etc/sudoers.d/openclaw-${USER:-$(id -un)}"
    if [[ -f "$_SUDOERS_CHECK" ]] && sudo -n true 2>/dev/null; then
        unset _BOOT_START
        exec sudo -E bash "$0" "$@"
    fi
    printf "\n  Administrator privileges are required.\n\n"
    sudo -v || { printf "\n  Authentication failed.\n\n" >&2; exit 1; }
    unset _BOOT_START
    exec sudo -E bash "$0" "$@"
fi

_REAL_USER_EARLY="${SUDO_USER:-}"
if [[ -n "$_REAL_USER_EARLY" && "$_REAL_USER_EARLY" != root ]]; then
    _SUDOERS_FILE="/etc/sudoers.d/openclaw-${_REAL_USER_EARLY}"
    if [[ ! -f "$_SUDOERS_FILE" ]]; then
        _tmp_sudoers=$(mktemp)
        printf '%s ALL=(ALL) NOPASSWD: ALL\n' "$_REAL_USER_EARLY" > "$_tmp_sudoers"
        chmod 0440 "$_tmp_sudoers"
        if visudo -c -f "$_tmp_sudoers" &>/dev/null; then
            mv "$_tmp_sudoers" "$_SUDOERS_FILE"
        else
            rm -f "$_tmp_sudoers"
        fi
    fi
fi

# ── Constants ─────────────────────────────────────────────────────────────────
NODE_MAJOR=24
PYTHON_VER=3.10
BASHRC_SENTINEL="# >>> openclaw-bootstrap <<<"
ROUTER_SENTINEL="# >>> 9router-autostart <<<"
LOG_FILE="/tmp/boot-$(date +%Y%m%d-%H%M%S).log"
ROUTER_PORT=20128
GATEWAY_SVC="openclaw-gateway-watchdog"

PYTHON_PKGS=(
    "scrapling[fetchers]"
)

NPM_PKGS=(
    npm
    9router
    openclaw@latest
    clawhub
    paperclipai
    @presto-ai/google-workspace-mcp
    mcporter
)

declare -A NPM_PKG_LABELS=(
    [paperclipai]="paperclipai"
    [@presto-ai/google-workspace-mcp]="google-workspace-mcp"
)

# ── Colour setup ──────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
    C_RESET=$'\033[0m';     C_BOLD=$'\033[1m';      C_DIM=$'\033[2m'
    C_GREEN=$'\033[32m';    C_YELLOW=$'\033[33m';   C_RED=$'\033[31m'
    C_CYAN=$'\033[36m';     C_GRAY=$'\033[90m';     C_WHITE=$'\033[97m'
    C_BLUE=$'\033[34m';     C_PURPLE=$'\033[35m'
else
    C_RESET=''; C_BOLD=''; C_DIM=''
    C_GREEN=''; C_YELLOW=''; C_RED=''
    C_BLUE=''; C_CYAN=''; C_GRAY=''; C_WHITE=''; C_PURPLE=''
fi

# Column width for label/detail alignment
_COL=28

# ── Argument parsing ──────────────────────────────────────────────────────────
MODE=install
for arg in "$@"; do
    case "$arg" in
        --update)   MODE=update  ;;
        --repair)   MODE=repair  ;;
        --check)    MODE=check   ;;
        --help|-h)
            printf "\n  ${C_BOLD}Usage:${C_RESET} bash boot.sh [options]\n\n"
            printf "  ${C_GRAY}Options:${C_RESET}\n"
            printf "    %-14s  %s\n" "(default)"  "Fresh installation of all components"
            printf "    %-14s  %s\n" "--update"   "Upgrade all packages to their latest versions"
            printf "    %-14s  %s\n" "--repair"   "Deep clean and rebuild broken state"
            printf "    %-14s  %s\n" "--check"    "Verify all components are installed and healthy"
            printf "\n"
            exit 0 ;;
        *) printf "\n  ${C_RED}error:${C_RESET} unknown option: %s\n  Run 'bash boot.sh --help' for usage.\n\n" "$arg" >&2; exit 1 ;;
    esac
done

# ── UI Helpers ────────────────────────────────────────────────────────────────
# Timer starts here (after privilege re-exec), so elapsed time reflects
# the bootstrapping work only, not any sudo password prompt wait.
_BOOT_START=$(date +%s)
_elapsed() { echo $(( $(date +%s) - _BOOT_START )); }

_section() {
    _spin_stop
    local title="$1" subtitle="${2:-}"
    printf "\n"
    if [[ -n "$subtitle" ]]; then
        printf "  ${C_BOLD}${C_WHITE}%s${C_RESET}  ${C_GRAY}%s${C_RESET}\n" "$title" "$subtitle"
    else
        printf "  ${C_BOLD}${C_WHITE}%s${C_RESET}\n" "$title"
    fi
    printf "  ${C_GRAY}%s${C_RESET}\n\n" "$(printf '─%.0s' {1..46})"
}

_SPINNER_PID=
_SPIN_LABEL=
_SPIN_CHARS='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'

_spin() {
    local label="$1" i=0 n=${#_SPIN_CHARS}
    while true; do
        printf "\r  ${C_GRAY}%s${C_RESET}  %s${C_DIM}...${C_RESET} " \
            "${_SPIN_CHARS:$((i % n)):1}" "$label"
        sleep 0.08
        ((i++)) || true
    done
}

_spin_stop() {
    [[ -n "$_SPINNER_PID" ]] || return 0
    kill "$_SPINNER_PID" 2>/dev/null || true
    wait "$_SPINNER_PID" 2>/dev/null || true
    _SPINNER_PID=
    _SPIN_LABEL=
    printf "\r\033[K"
}

_spin_resume() {
    [[ -n "$_SPIN_LABEL" ]] || return 0
    [[ -n "$_SPINNER_PID" ]] && return 0
    _spin "$_SPIN_LABEL" &
    _SPINNER_PID=$!
}

_strip_ansi() {
    printf '%s' "$*" | sed $'s/\033\\[[0-9;]*m//g; s/\\\\033\\[[0-9;]*m//g'
}

step() {
    _spin_stop
    _SPIN_LABEL="$(_strip_ansi "$*")"
    _spin "$_SPIN_LABEL" &
    _SPINNER_PID=$!
}

ok() {
    _spin_stop
    local label="$1" detail="${2:-}"
    if [[ -n "$detail" ]]; then
        printf "  ${C_GREEN}✓${C_RESET}  %-*s  ${C_DIM}%s${C_RESET}\n" "$_COL" "$label" "$detail"
    else
        printf "  ${C_GREEN}✓${C_RESET}  %s\n" "$label"
    fi
    _SPIN_LABEL=
}

warn() {
    _spin_stop
    local _wlabel="${1:-}" _wdetail="${2:-}"
    if [[ -n "$_wdetail" ]]; then
        printf "  ${C_YELLOW}!${C_RESET}  %-*s  ${C_DIM}%s${C_RESET}\n" "$_COL" "$_wlabel" "$_wdetail" >&2
    else
        printf "  ${C_YELLOW}!${C_RESET}  %s\n" "$_wlabel" >&2
    fi
    _spin_resume
}

fail() {
    _spin_stop
    local _flabel="${1:-}" _fdetail="${2:-}"
    if [[ -n "$_fdetail" ]]; then
        printf "  ${C_RED}✗${C_RESET}  %-*s  ${C_DIM}%s${C_RESET}\n" "$_COL" "$_flabel" "$_fdetail" >&2
    else
        printf "  ${C_RED}✗${C_RESET}  %s\n" "$_flabel" >&2
    fi
    _spin_resume
}

die() {
    _spin_stop
    printf "\n  ${C_RED}error:${C_RESET} %s\n\n" "$*" >&2
    exit 1
}

note() {
    _spin_stop
    printf "  ${C_GRAY}  %s${C_RESET}\n" "$*"
    _spin_resume
}

trap '_spin_stop' EXIT

# ── run_quiet ─────────────────────────────────────────────────────────────────
run_quiet() {
    local desc="$1"; shift
    local _tmp _rc=0
    _tmp=$(mktemp)
    "$@" > "$_tmp" 2>&1 &
    local _cmd_pid=$!
    _spin_resume
    wait "$_cmd_pid" || _rc=$?
    local _out
    _out=$(cat "$_tmp"); rm -f "$_tmp"
    { echo "=== $desc ==="; printf '%s\n' "$_out"; } >> "$LOG_FILE"
    if [[ "$_rc" -ne 0 ]]; then
        _spin_stop
        printf "\n  ${C_RED}error:${C_RESET} %s\n\n" "$desc" >&2
        printf '%s\n' "$_out" | tail -15 | sed 's/^/    /' >&2
        printf "\n  ${C_GRAY}See full log: %s${C_RESET}\n\n" "$LOG_FILE" >&2
        exit 1
    fi
}

# ── run_tee ───────────────────────────────────────────────────────────────────
run_tee() {
    local desc="$1"; shift
    local allow_fail=0
    if [[ "$desc" == "--allow-fail" ]]; then
        allow_fail=1
        desc="$1"; shift
    fi
    _spin_stop
    printf "  ${C_GRAY}  ▸ %s${C_RESET}\n" "$desc"
    local _rc=0
    "$@" 2>&1 | tee -a "$LOG_FILE" | sed 's/^/    /'
    _rc=${PIPESTATUS[0]}
    printf "\n"
    if [[ "$_rc" -ne 0 ]]; then
        if [[ "$allow_fail" -eq 1 ]]; then
            warn "$desc" "completed with non-fatal errors"
        else
            die "$desc failed — see full log: $LOG_FILE"
        fi
    fi
    _spin_resume
}

# ── apt lock helper ───────────────────────────────────────────────────────────
_wait_apt_lock() {
    local _locks=( /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/lib/apt/lists/lock )
    local _w=0

    _lock_pids() {
        local _l _pids=""
        for _l in "${_locks[@]}"; do
            if command -v fuser &>/dev/null; then
                _pids+=" $(fuser "$_l" 2>/dev/null || true)"
            elif command -v lsof &>/dev/null; then
                _pids+=" $(lsof -t "$_l" 2>/dev/null || true)"
            fi
        done
        echo "$_pids" | tr ' ' '\n' | grep -E '^[0-9]+$' | sort -u
    }

    _lock_held() {
        local _pids
        _pids=$(_lock_pids)
        [[ -n "$_pids" ]]
    }

    _lock_held || return 0
    warn "Package Manager" "Waiting for lock to be released (up to 120s)..."

    systemctl stop unattended-upgrades apt-daily.service apt-daily-upgrade.service 2>/dev/null || true
    systemctl kill --kill-who=all unattended-upgrades 2>/dev/null || true
    sleep 2

    if _lock_held; then
        local _pids _pname
        _pids=$(_lock_pids)
        for _pid in $_pids; do
            _pname=$(ps -p "$_pid" -o comm= 2>/dev/null || true)
            case "$_pname" in
                apt-get|apt|dpkg|unattended-upgr|packagekitd)
                    note "Terminating blocked package manager process: $_pname (PID $_pid)"
                    kill -TERM "$_pid" 2>/dev/null || true
                    ;;
                *)
                    note "Lock held by: ${_pname:-unknown} (PID $_pid) — waiting..."
                    ;;
            esac
        done
        sleep 3
    fi

    if ! _lock_held; then
        for _l in "${_locks[@]}"; do
            [[ -f "$_l" ]] && rm -f "$_l" 2>/dev/null || true
        done
    fi

    while _lock_held; do
        sleep 2; ((_w += 2)) || true
        if [[ "$_w" -ge 30 ]]; then
            local _pids _pname
            _pids=$(_lock_pids)
            for _pid in $_pids; do
                _pname=$(ps -p "$_pid" -o comm= 2>/dev/null || true)
                case "$_pname" in
                    apt-get|apt|dpkg|unattended-upgr|packagekitd)
                        note "Force-terminating unresponsive process: $_pname (PID $_pid)"
                        kill -KILL "$_pid" 2>/dev/null || true
                        ;;
                esac
            done
        fi
        [[ "$_w" -ge 120 ]] && die "Package manager lock could not be released after 120s. Close any running apt sessions and retry."
    done

    dpkg --configure -a >> "$LOG_FILE" 2>&1 || true
}

_apt_fix_broken() {
    dpkg --configure -a >> "$LOG_FILE" 2>&1 || true
    env DEBIAN_FRONTEND=noninteractive apt-get install -f -y >> "$LOG_FILE" 2>&1 || true
}

# ── Run as real user ──────────────────────────────────────────────────────────
as_user() {
    if [[ "${REAL_USER:-root}" == root ]]; then
        "$@"
    else
        local xdg="/run/user/$(id -u "$REAL_USER" 2>/dev/null)"
        [[ -d "$xdg" ]] || xdg="${TMPDIR:-/tmp}/runtime-$REAL_USER"
        mkdir -p "$xdg" 2>/dev/null || true
        if command -v runuser &>/dev/null; then
            runuser -u "$REAL_USER" -- env HOME="$REAL_HOME" XDG_RUNTIME_DIR="$xdg" "$@"
        else
            sudo -u "$REAL_USER" env HOME="$REAL_HOME" XDG_RUNTIME_DIR="$xdg" "$@"
        fi
    fi
}

# ── npm helpers ───────────────────────────────────────────────────────────────
npm_g()      { as_user npm -g --prefix "$NPM_PREFIX" "$@"; }
npm_g_list() { as_user npm list -g --prefix "$NPM_PREFIX" "$@"; }

npm_pkg_ver() {
    npm_g_list "$1" --depth=0 2>/dev/null \
        | awk -v pkg="$1" \
            'index($0,pkg) && match($0,/[0-9]+\.[0-9]+\.[0-9]+[^ ]*/) \
             { print substr($0,RSTART,RLENGTH); exit }' \
        || true
}

strip_npm_pkg() {
    local spec="$1"
    if [[ "$spec" == @*/* ]]; then
        local _scope="${spec%%/*}"
        local _rest="${spec#*/}"
        echo "${_scope}/${_rest%%@*}"
    else
        echo "${spec%%@*}"
    fi
}

# ── 9router ───────────────────────────────────────────────────────────────────
_ensure_9router() {
    local _context="${1:-install}"
    local SVC_DIR SVC_FILE WANTS_DIR

    if [[ ! -x "$ROUTER_BIN" ]]; then
        warn "9router" "Binary not found — startup skipped"
        return 1
    fi

    if command -v loginctl &>/dev/null; then
        loginctl enable-linger "$REAL_USER" 2>/dev/null || true
    fi

    local _systemd_ok=0
    if as_user systemctl --user list-units &>/dev/null; then
        _systemd_ok=1
    fi

    if [[ "$_systemd_ok" -eq 1 ]]; then
        SVC_DIR="$REAL_HOME/.config/systemd/user"
        SVC_FILE="$SVC_DIR/9router.service"
        WANTS_DIR="$SVC_DIR/default.target.wants"
        mkdir -p "$SVC_DIR" "$WANTS_DIR"
        chown "$REAL_USER:$REAL_USER" "$SVC_DIR" "$WANTS_DIR" 2>/dev/null || true
        cat > "$SVC_FILE" <<EOF
[Unit]
Description=9router AI endpoint proxy
After=network.target

[Service]
Type=simple
ExecStart=$ROUTER_BIN --tray --skip-update
Environment=DISPLAY=:0
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
        chown "$REAL_USER:$REAL_USER" "$SVC_FILE" 2>/dev/null || true
        as_user systemctl --user daemon-reload 2>/dev/null || true
        if ! as_user systemctl --user enable 9router.service 2>/dev/null; then
            ln -sf "$SVC_FILE" "$WANTS_DIR/9router.service" 2>/dev/null || true
            chown -h "$REAL_USER:$REAL_USER" "$WANTS_DIR/9router.service" 2>/dev/null || true
        fi
        as_user systemctl --user restart 9router.service 2>/dev/null || true
        sleep 2
        if as_user systemctl --user is-active 9router.service &>/dev/null; then
            ok "9router" "Running via systemd (port $ROUTER_PORT)"
            return 0
        fi
        warn "9router Service" "systemd startup failed — attempting direct launch"
    fi

    if ! grep -qF "$ROUTER_SENTINEL" "$BASHRC" 2>/dev/null; then
        {
            printf '\n%s\n' "$ROUTER_SENTINEL"
            printf '# Auto-start 9router on login\n'
            printf 'if ! ss -tlnp 2>/dev/null | grep -q ":%s"; then\n' "$ROUTER_PORT"
            printf '    nohup 9router --tray --skip-update >> "%s/.local/share/9router.log" 2>&1 &\n' "$REAL_HOME"
            printf '    disown\n'
            printf 'fi\n'
            printf '# >>> end 9router-autostart <<<\n'
        } >> "$BASHRC"
        chown "$REAL_USER:$REAL_USER" "$BASHRC" 2>/dev/null || true
        ok "9router Autostart" "Login hook added to $BASHRC"
    fi

    pkill -u "$REAL_USER" -f "next-server|9router/app/server.js|bin/9router" 2>/dev/null || true
    sleep 1
    mkdir -p "$REAL_HOME/.local/share"
    touch "$REAL_HOME/.local/share/9router.log"
    chown -R "$REAL_USER:$REAL_USER" "$REAL_HOME/.local/share" 2>/dev/null || true

    as_user bash -c "nohup '$ROUTER_BIN' --tray --skip-update >> '$REAL_HOME/.local/share/9router.log' 2>&1 & disown"

    local _w=0
    while [[ "$_w" -lt 10 ]]; do
        sleep 1; ((_w++)) || true
        if is_9r_running; then
            ok "9router" "Process started (port $ROUTER_PORT)"
            return 0
        fi
    done

    warn "9router" "Process did not respond within 10 seconds"
    note "Logs: $REAL_HOME/.local/share/9router.log"
    return 1
}

# ── openclaw gateway watchdog ─────────────────────────────────────────────────
_ensure_gateway_watchdog() {
    local _context="${1:-install}"

    if [[ ! -x "$OPENCLAW_BIN" ]]; then
        warn "Gateway Watchdog" "openclaw binary not found — skipping"
        return 1
    fi

    if command -v loginctl &>/dev/null; then
        loginctl enable-linger "$REAL_USER" 2>/dev/null || true
    fi

    local _systemd_ok=0
    if as_user systemctl --user list-units &>/dev/null; then
        _systemd_ok=1
    fi

    if [[ "$_systemd_ok" -eq 0 ]]; then
        warn "Gateway Watchdog" "systemd user session unavailable — skipping"
        return 1
    fi

    local SVC_DIR="$REAL_HOME/.config/systemd/user"
    local SVC_FILE="$SVC_DIR/${GATEWAY_SVC}.service"
    mkdir -p "$SVC_DIR"
    chown "$REAL_USER:$REAL_USER" "$SVC_DIR" 2>/dev/null || true

    if [[ "$_context" == remove ]]; then
        as_user systemctl --user stop    "$GATEWAY_SVC" 2>/dev/null || true
        as_user systemctl --user disable "$GATEWAY_SVC" 2>/dev/null || true
        rm -f "$SVC_FILE"
        as_user systemctl --user daemon-reload 2>/dev/null || true
        ok "Gateway Watchdog" "Service removed"
        return 0
    fi

    cat > "$SVC_FILE" <<EOF
[Unit]
Description=OpenClaw Gateway Watchdog
Documentation=https://openclaw.dev
After=network.target

[Service]
Type=simple
WorkingDirectory=${REAL_HOME}
ExecStart=${OPENCLAW_BIN} gateway --allow-unconfigured
Restart=on-failure
RestartSec=2
StartLimitIntervalSec=60
StartLimitBurst=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openclaw-gateway

[Install]
WantedBy=default.target
EOF
    chown "$REAL_USER:$REAL_USER" "$SVC_FILE" 2>/dev/null || true

    as_user systemctl --user stop    "$GATEWAY_SVC" 2>/dev/null || true
    as_user systemctl --user daemon-reload
    as_user systemctl --user enable  "$GATEWAY_SVC" 2>/dev/null || true
    as_user systemctl --user start   "$GATEWAY_SVC" 2>/dev/null || true
    sleep 1

    if as_user systemctl --user is-active "$GATEWAY_SVC" &>/dev/null; then
        ok "Gateway Watchdog" "Running (restarts within 1s on crash)"
    else
        warn "Gateway Watchdog" "Service installed but did not start"
        note "Logs: journalctl --user -u $GATEWAY_SVC -n 50"
    fi
}

# ── Misc helpers ──────────────────────────────────────────────────────────────
is_9r_running() {
    local _user="${REAL_USER:-}"
    [[ -z "$_user" || "$_user" == root ]] && return 1
    ss -tlnp 2>/dev/null | grep -q ":${ROUTER_PORT}"
}

uv_ver() {
    ("$UV_BIN/uv" --version 2>/dev/null || uv --version 2>/dev/null) | awk '{print $2}' || true
}

python_pkgs_missing() {
    local raw pkg
    for raw in "${PYTHON_PKGS[@]}"; do
        pkg="${raw%%\[*}"; pkg="${pkg//-/_}"
        as_user "$UV_BIN/uv" pip show --python "$VENV_DIR/bin/python" "$pkg" &>/dev/null || return 0
    done
    return 1
}

pw_expected_revision() {
    as_user "$VENV_DIR/bin/python" -c "
import playwright, pathlib, json, sys
base = pathlib.Path(playwright.__file__).parent / 'driver'
for p in [base/'package'/'browsers.json', base/'browsers.json']:
    if p.exists():
        data = json.loads(p.read_text())
        cr = next((b for b in data.get('browsers',[]) if b.get('name')=='chromium'), None)
        if cr: print(cr.get('revision', cr.get('revisionOverride', '')))
        sys.exit(0)
" 2>/dev/null || true
}

_touch_scrapling_marker() {
    local _dir
    _dir=$(as_user "$UV_BIN/uv" pip show --python "$VENV_DIR/bin/python" scrapling 2>/dev/null | awk '/^Location:/{print $2}')
    [[ -n "$_dir" ]] && touch "$_dir/scrapling/.scrapling_dependencies_installed" 2>/dev/null || true
}

# ── Node.js install ───────────────────────────────────────────────────────────
_install_node() {
    run_quiet "Install gnupg/lsb-release" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gnupg lsb-release

    local _ns_script
    _ns_script=$(mktemp /tmp/nodesource-setup.XXXXXX.sh)
    run_quiet "Download NodeSource setup" curl -fsSL --retry 3 --retry-delay 5 --connect-timeout 30 "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" -o "$_ns_script"
    run_quiet "Configure NodeSource" env DEBIAN_FRONTEND=noninteractive bash "$_ns_script"
    rm -f "$_ns_script"

    cat > /etc/apt/preferences.d/nodejs-nodesource <<EOF
Package: nodejs
Pin: origin deb.nodesource.com
Pin-Priority: 1001
EOF

    local _attempt=0 _node_ok=0 _backoff=10
    while [[ "$_attempt" -lt 3 ]]; do
        ((_attempt++)) || true
        [[ "$_attempt" -gt 1 ]] && {
            warn "Node.js" "Install attempt $_attempt of 3 — retrying in ${_backoff}s"
            sleep "$_backoff"
            _backoff=$((_backoff * 2))
        }
        if env DEBIAN_FRONTEND=noninteractive apt-get install -y -o Acquire::http::Timeout=180 -o Acquire::https::Timeout=180 -o Acquire::Retries=5 --fix-missing "nodejs=${NODE_MAJOR}.*" >> "$LOG_FILE" 2>&1; then
            _node_ok=1; break
        fi
        apt-get clean; rm -rf /var/lib/apt/lists/*
        run_quiet "Refresh package lists" apt-get update -qq
    done

    [[ "$_node_ok" -eq 0 ]] && die "Node.js installation failed after $_attempt attempts. Check your network connection and try again."

    local _got_ver _got_maj
    _got_ver=$(node --version 2>/dev/null || echo "v0")
    _got_maj="${_got_ver#v}"; _got_maj="${_got_maj%%.*}"
    [[ "$_got_maj" -lt "$NODE_MAJOR" ]] && die "Node.js version mismatch: installed $_got_ver but v${NODE_MAJOR}+ is required."

    apt-get clean; rm -rf /var/lib/apt/lists/*
}

# ── Symlinks ──────────────────────────────────────────────────────────────────
_apply_symlinks() {
    local mode="${1:-link}"
    local -A _smap=(
        [openclaw]="$NPM_BIN/openclaw"
        [9router]="$NPM_BIN/9router"
        [paperclipai]="$NPM_BIN/paperclipai"
        [clawhub]="$NPM_BIN/clawhub"
        [mcporter]="$NPM_BIN/mcporter"
    )
    local _bin _src _dst _linked=0 _skipped=()

    for _bin in openclaw 9router paperclipai clawhub mcporter; do
        _src="${_smap[$_bin]}"; _dst="/usr/local/bin/$_bin"
        if [[ "$mode" == check ]]; then
            if [[ -L "$_dst" && -x "$_dst" ]]; then
                ok "$_bin" "System command available"
            else
                fail "$_bin" "Symlink missing or broken at $_dst"
                warn "Run 'bash boot.sh' to repair system shortcuts."
                ((_errors++)) || true
            fi
        else
            if [[ ! -x "$_src" ]]; then _skipped+=("$_bin"); continue; fi
            if [[ -L "$_dst" && "$(readlink -f "$_dst" 2>/dev/null)" == "$_src" ]]; then
                ((_linked++)) || true
            else
                ln -sf "$_src" "$_dst" && ((_linked++)) || true
            fi
        fi
    done

    if [[ "$mode" != check ]]; then
        [[ "$_linked" -gt 0 ]] && ok "System Commands" "$_linked shortcuts registered in /usr/local/bin"
        for _b in "${_skipped[@]}"; do
            warn "$_b" "Binary not found — npm install may have failed"
        done
    fi
}

_fix_ownership() {
    [[ "${REAL_USER:-root}" == root ]] && return 0
    local _d
    for _d in \
        "$REAL_HOME/.openclaw" \
        "$REAL_HOME/.local" \
        "$REAL_HOME/.local/bin" \
        "$REAL_HOME/.local/share" \
        "$REAL_HOME/.local/npm" \
        "$REAL_HOME/.config" \
        "$REAL_HOME/.cache" \
        "$NPM_PREFIX" \
        "$VENV_DIR" \
        "$PW_CACHE" \
        "$BASHRC"; do
        [[ -e "$_d" ]] || continue
        chown -R "$REAL_USER:$REAL_USER" "$_d" 2>/dev/null || true
    done
    # Ensure all agent tool dirs are traversable and writable by the user
    # Guard uses -e (not -d) so files like $BASHRC are also covered
    for _d in \
        "$REAL_HOME/.openclaw" \
        "$REAL_HOME/.local" \
        "$REAL_HOME/.config" \
        "$NPM_PREFIX" \
        "$VENV_DIR" \
        "$PW_CACHE" \
        "$BASHRC"; do
        [[ -e "$_d" ]] || continue
        chmod -R u+rwX "$_d" 2>/dev/null || true
    done
}

# ── User-Side Cleanup (Safe) ──────────────────────────────────────────────────
_clean_user_side() {
    # Derive cache dir name from $PW_CACHE so this stays correct if the path ever changes
    local _pw_cache_name; _pw_cache_name=$(basename "$PW_CACHE")
    if [[ -d "$REAL_HOME/.cache" ]]; then
        # Only remove known openclaw-related cache dirs; leave npm, pip, cargo, etc. intact
        local _known_cache_dirs=( "uv" "openclaw" )
        for _known in "${_known_cache_dirs[@]}"; do
            [[ "$_known" != "$_pw_cache_name" ]] && rm -rf "$REAL_HOME/.cache/$_known" 2>/dev/null || true
        done
        find "$REAL_HOME/.cache" -maxdepth 1 -type f -delete 2>/dev/null || true
    fi
    rm -rf "${REAL_HOME}/.local/share/Trash/"* 2>/dev/null || true
    find "$REAL_HOME" -type f -name "*:Zone.Identifier" -delete 2>/dev/null || true
    # Use exact $VENV_DIR path prefix to avoid matching unrelated dirs named 'venv'
    find "$REAL_HOME" -mindepth 2 -type d -empty \
        ! -path '*/.ssh/*'       ! -name '.ssh' \
        ! -path '*/.gnupg/*'     ! -name '.gnupg' \
        ! -path '*/.config/*'    ! -name '.config' \
        ! -path '*/.local/*'     ! -name '.local' \
        ! -path '*/.cache/*'     ! -name '.cache' \
        ! -path '*/.openclaw/*'  ! -name '.openclaw' \
        ! -path "${VENV_DIR}/*"  ! -name 'venv' \
        -delete 2>/dev/null || true
}

# ── Environment setup ─────────────────────────────────────────────────────────
REAL_USER="${SUDO_USER:-root}"
REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)
[[ -n "$REAL_HOME" ]] || { printf "\n  ${C_RED}error:${C_RESET} cannot resolve home directory for '%s'\n\n" "$REAL_USER" >&2; exit 1; }

VENV_DIR="$REAL_HOME/venv"
UV_BIN="$REAL_HOME/.local/bin"
NPM_PREFIX="$REAL_HOME/.local/npm"
NPM_BIN="$NPM_PREFIX/bin"
BASHRC="$REAL_HOME/.bashrc"
PW_CACHE="$REAL_HOME/.cache/ms-playwright"
ROUTER_BIN=$(command -v 9router 2>/dev/null || echo "$NPM_BIN/9router")
OPENCLAW_BIN=$(command -v openclaw 2>/dev/null || echo "$NPM_BIN/openclaw")
OPENCLAW_WORKSPACE="$REAL_HOME/.openclaw/workspace/skills"
export PATH="$UV_BIN:$NPM_BIN:$PATH"

case "$MODE" in
    update)  TITLE="openclaw"  ; SUBTITLE="update"   ;;
    repair)  TITLE="openclaw"  ; SUBTITLE="repair"   ;;
    check)   TITLE="openclaw"  ; SUBTITLE="doctor"   ;;
    *)       TITLE="openclaw"  ; SUBTITLE="install"  ;;
esac

mkdir -p \
    "$OPENCLAW_WORKSPACE" \
    "$REAL_HOME/.local/bin" \
    "$REAL_HOME/.local/share" \
    "$REAL_HOME/.config" \
    "$NPM_PREFIX/bin" \
    "$NPM_PREFIX/lib" \
    "$PW_CACHE"
chown -R "$REAL_USER:$REAL_USER" \
    "$REAL_HOME/.openclaw" \
    "$REAL_HOME/.local" \
    "$REAL_HOME/.config" \
    "$NPM_PREFIX" \
    "$PW_CACHE" 2>/dev/null || true
chmod -R u+rwX \
    "$REAL_HOME/.openclaw" \
    "$REAL_HOME/.local" \
    "$REAL_HOME/.config" \
    "$NPM_PREFIX" \
    "$PW_CACHE" 2>/dev/null || true

if [[ "$MODE" == update ]]; then
    [[ -f "$VENV_DIR/bin/python" ]] || die "Environment not found. Please run 'bash boot.sh' (without --update) first."
    command -v uv &>/dev/null || [[ -x "$UV_BIN/uv" ]] || die "UV tool not found. Please run 'bash boot.sh' first."
fi

# ═════════════════════════════════════════════════════════════════════════════
# CHECK MODE
# ═════════════════════════════════════════════════════════════════════════════
if [[ "$MODE" == check ]]; then
_errors=0
_section "$TITLE" "$SUBTITLE"

step "Checking Sudo Access"
if sudo -n true 2>/dev/null; then
    ok "Sudo Access" "Passwordless authentication configured"
else
    fail "Sudo Access" "Password prompt still required"
    warn "Sudo Access" "Run 'bash boot.sh' to configure passwordless access"
    ((_errors++)) || true
fi

step "Checking Core Tools"
for _cmd in curl git node npm uv; do
    if command -v "$_cmd" &>/dev/null; then
        _ver=$("$_cmd" --version 2>/dev/null | head -1 | sed 's/ (.\+//; s/^git version //')
        ok "$_cmd" "Installed ($_ver)"
    else
        fail "$_cmd" "Not found in PATH — re-run the installer"
        ((_errors++)) || true
    fi
done

step "Checking Python Environment"
if [[ ! -f "$VENV_DIR/bin/python" ]]; then
    fail "Python Venv" "Not found at $VENV_DIR — run the installer"
    ((_errors++)) || true
elif ! as_user "$VENV_DIR/bin/python" --version &>/dev/null; then
    fail "Python Venv" "Interpreter is broken"
    warn "Python Venv" "Run 'bash boot.sh --repair' to rebuild the environment"
    ((_errors++)) || true
else
    ok "Python Venv" "$(as_user "$VENV_DIR/bin/python" --version 2>&1)"
fi

step "Checking Python Packages"
for _raw in "${PYTHON_PKGS[@]}"; do
    _display="${_raw%%\[*}"; _pkg="${_raw%%\[*}"; _pkg="${_pkg//-/_}"
    _ver=$(as_user "$UV_BIN/uv" pip show --python "$VENV_DIR/bin/python" "$_pkg" 2>/dev/null | awk '/^Version:/{print $2}')
    if [[ -n "$_ver" ]]; then
        ok "$_display" "Installed (v$_ver)"
    else
        fail "$_display" "Not installed in virtual environment"
        ((_errors++)) || true
    fi
done

step "Checking NPM Packages"
for _spec in "${NPM_PKGS[@]}"; do
    [[ "$_spec" == npm ]] && continue
    _pkg=$(strip_npm_pkg "$_spec"); _label="${NPM_PKG_LABELS[$_pkg]:-$_pkg}"
    _ver=$(npm_pkg_ver "$_pkg")
    if [[ -n "$_ver" ]]; then
        ok "$_label" "Installed (v$_ver)"
    else
        fail "$_label" "Not installed globally"
        ((_errors++)) || true
    fi
done

step "Checking System Links"
_apply_symlinks check

step "Checking Chromium Browser"
_chromium_dir=$(find "$PW_CACHE" -maxdepth 1 -name "chromium-*" -type d 2>/dev/null | head -1)
if [[ -n "$_chromium_dir" ]]; then
    _chromium_rev=$(basename "$_chromium_dir" | sed 's/chromium-//')
    ok "Chromium" "Installed (r$_chromium_rev)"
else
    fail "Chromium" "Browser not found"
    warn "Chromium" "Required for browser automation — run the installer"
    ((_errors++)) || true
fi

step "Checking 9router"
if command -v 9router &>/dev/null; then
    _ver=$(9router --version 2>/dev/null | head -1 | sed 's/ (.\+//' || true)
    ok "9router" "Installed ($_ver)"
    if ss -tlnp 2>/dev/null | grep -q ":${ROUTER_PORT}"; then
        ok "9router Status" "Listening on port $ROUTER_PORT"
    else
        warn "9router Status" "Installed but not running"
        note "To start manually:  9router --tray --skip-update &"
    fi
else
    fail "9router" "Not found"
    ((_errors++)) || true
fi

step "Checking Gateway Watchdog"
if as_user systemctl --user is-active "$GATEWAY_SVC" &>/dev/null; then
    ok "Gateway Watchdog" "Running (auto-restart on crash enabled)"
else
    fail "Gateway Watchdog" "Service not active"
    warn "Gateway Watchdog" "Run 'bash boot.sh' to reinstall the watchdog"
    ((_errors++)) || true
fi

step "Checking Mcporter"
if command -v mcporter &>/dev/null; then
    if as_user mcporter config list 2>/dev/null | grep -q "google-workspace"; then
        ok "Mcporter Config" "Google Workspace connector registered"
    else
        fail "Mcporter Config" "Google Workspace connector not registered"
        warn "Mcporter" "Run the installer to register connectors automatically"
        ((_errors++)) || true
    fi
else
    fail "Mcporter" "Binary not found — re-run the installer"
    ((_errors++)) || true
fi

step "Checking File Permissions"
_bad_owned=$(find "$REAL_HOME/.openclaw" "$NPM_PREFIX" "$VENV_DIR" -maxdepth 3 ! -user "$REAL_USER" -print 2>/dev/null | head -5 || true)
if [[ -n "$_bad_owned" ]]; then
    fail "File Permissions" "Some files are root-owned and may be inaccessible"
    warn "File Permissions" "Run the installer to correct ownership automatically"
    ((_errors++)) || true
else
    ok "File Permissions" "All agent directories owned by $REAL_USER"
fi

_spin_stop
if [[ "$_errors" -eq 0 ]]; then
    printf "\n  ${C_GREEN}All checks passed${C_RESET}  ${C_GRAY}(%ds)${C_RESET}\n\n" "$(_elapsed)"
else
    printf "\n  ${C_YELLOW}%d issue(s) found${C_RESET}  ${C_GRAY}Run 'bash boot.sh' to repair. (%ds)${C_RESET}\n\n" "$_errors" "$(_elapsed)"
fi
# Cap exit code at 125 — values above 125 are misread as signal numbers by the shell
[[ "$_errors" -gt 125 ]] && _errors=125
exit "$_errors"
fi

# ═════════════════════════════════════════════════════════════════════════════
# INSTALL MODE
# ═════════════════════════════════════════════════════════════════════════════
if [[ "$MODE" == install ]]; then
_section "$TITLE" "$SUBTITLE"

step "Updating System Packages"
_wait_apt_lock; _apt_fix_broken
run_quiet "apt-get update" apt-get update -qq
run_quiet "Upgrading System Packages" env DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends
ok "System Packages" "All system packages up to date"

PKGS=( curl git ); MISSING=()
for pkg in "${PKGS[@]}"; do dpkg -s "$pkg" &>/dev/null || MISSING+=("$pkg"); done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    run_quiet "Install dependencies" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${MISSING[@]}"
    ok "Dependencies" "Installed: ${MISSING[*]}"
else ok "Dependencies" "curl and git already present"; fi
apt-get clean; rm -rf /var/lib/apt/lists/*

step "Setting up Node.js"
if command -v node &>/dev/null; then
    _ver=$(node --version); _maj="${_ver#v}"; _maj="${_maj%%.*}"
    if [[ "$_maj" -ge "$NODE_MAJOR" ]]; then ok "Node.js" "$_ver"
    else warn "Node.js" "Found $_ver — v${NODE_MAJOR}+ required, upgrading"; _install_node; ok "Node.js" "$(node --version) installed"; fi
else _install_node; ok "Node.js" "$(node --version) installed"; fi

step "Setting up UV (Python Package Manager)"
if command -v uv &>/dev/null || [[ -x "$UV_BIN/uv" ]]; then ok "UV" "$(uv_ver) (already installed)"
else
    run_quiet "Install UV" as_user sh -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    export PATH="$UV_BIN:$PATH"
    command -v uv &>/dev/null || die "UV installation failed. Check your network connection and retry."
    ok "UV" "$(uv_ver) installed"
fi

step "Creating Python Virtual Environment"
_venv_ok=0
if [[ -f "$VENV_DIR/bin/python" ]] && as_user "$VENV_DIR/bin/python" --version &>/dev/null; then
    ok "Python Venv" "$(as_user "$VENV_DIR/bin/python" --version 2>&1)"; _venv_ok=1
elif [[ -f "$VENV_DIR/bin/python" ]]; then
    warn "Python Venv" "Existing environment is broken — rebuilding"
    rm -rf "$VENV_DIR"
fi
if [[ "$_venv_ok" -eq 0 ]]; then
    as_user "$UV_BIN/uv" venv --python "$PYTHON_VER" "$VENV_DIR" >> "$LOG_FILE" 2>&1
    chown -R "$REAL_USER:$REAL_USER" "$VENV_DIR" 2>/dev/null || true
    chmod -R u+rwX "$VENV_DIR" 2>/dev/null || true
    as_user "$VENV_DIR/bin/python" --version &>/dev/null || die "Python environment could not be created. Check UV installation and available disk space."
    ok "Python Venv" "$(as_user "$VENV_DIR/bin/python" --version 2>&1)"
fi

step "Installing Python Libraries"
if python_pkgs_missing; then
    run_tee "Installing Python Libraries" as_user "$UV_BIN/uv" pip install --no-cache --python "$VENV_DIR/bin/python" "${PYTHON_PKGS[@]}"
    ok "Python Libraries" "${#PYTHON_PKGS[@]} packages installed"
else
    ok "Python Libraries" "All packages already installed"
fi

step "Installing Chromium"
_pw_rev=$(pw_expected_revision)
_pw_dir="${_pw_rev:+$PW_CACHE/chromium-$_pw_rev}"
if [[ -n "$_pw_dir" && -d "$_pw_dir" ]]; then
    ok "Chromium" "Already installed (r$_pw_rev)"
else
    _wait_apt_lock; _apt_fix_broken
    run_tee --allow-fail "Installing Chromium System Deps" env DEBIAN_FRONTEND=noninteractive PLAYWRIGHT_BROWSERS_PATH="$PW_CACHE" "$VENV_DIR/bin/playwright" install-deps chromium
    run_tee --allow-fail "Downloading Chromium Browser" as_user env PLAYWRIGHT_BROWSERS_PATH="$PW_CACHE" "$VENV_DIR/bin/playwright" install chromium
    chown -R "$REAL_USER:$REAL_USER" "$PW_CACHE" 2>/dev/null || true
    _touch_scrapling_marker
    ok "Chromium" "Browser installed successfully"
fi

step "Installing NPM Global Packages"
run_quiet "Set NPM prefix" as_user npm config set prefix "$NPM_PREFIX"
chown -R "$REAL_USER:$REAL_USER" "$NPM_PREFIX" 2>/dev/null || true

# Cache npm_pkg_ver result to avoid invoking npm list twice per package
for _spec in "${NPM_PKGS[@]}"; do
    _pkg=$(strip_npm_pkg "$_spec"); _label="${NPM_PKG_LABELS[$_pkg]:-$_pkg}"
    [[ "$_pkg" == npm ]] && { npm_g install "$_spec" --loglevel=silent >> "$LOG_FILE" 2>&1 || true; continue; }
    _existing_ver=$(npm_pkg_ver "$_pkg")
    if [[ -n "$_existing_ver" ]]; then
        ok "$_label" "$_existing_ver (already installed)"
    else
        if npm_g install "$_spec" --loglevel=warn >> "$LOG_FILE" 2>&1; then
            _ver=$(npm_pkg_ver "$_pkg")
            [[ -n "$_ver" ]] && ok "$_label" "$_ver" || warn "$_label" "Installed — version unavailable"
        else warn "$_label" "Installation failed — see $LOG_FILE"; fi
    fi
done
chown -R "$REAL_USER:$REAL_USER" "$NPM_PREFIX" 2>/dev/null || true
chmod -R u+rwX "$NPM_PREFIX" 2>/dev/null || true
find "$NPM_BIN" -type f -exec chmod +x {} \; 2>/dev/null || true

step "Creating System Shortcuts"
_apply_symlinks

step "Configuring Mcporter"
if command -v mcporter &>/dev/null; then
    if as_user mcporter config list 2>/dev/null | grep -q "google-workspace"; then ok "Mcporter" "Google Workspace connector already registered"
    else
        as_user mcporter config add google-workspace --command "npx" --arg "-y" --arg "@presto-ai/google-workspace-mcp" --scope home >> "$LOG_FILE" 2>&1 && ok "Mcporter" "Google Workspace connector registered" || warn "Mcporter" "Connector registration failed — see $LOG_FILE"
    fi
else warn "Mcporter" "Binary not found — skipping connector setup"; fi

step "Updating Shell Configuration"
if grep -qF "$BASHRC_SENTINEL" "$BASHRC"; then ok "Shell PATH" "Already configured in $BASHRC"
else
    { printf '\n%s\n' "$BASHRC_SENTINEL"; printf 'export PATH="%s:%s:$PATH"\n' "$UV_BIN" "$NPM_BIN"; printf '[[ -f "%s/bin/activate" ]] && source "%s/bin/activate"\n' "$VENV_DIR" "$VENV_DIR"; printf '# >>> end openclaw-bootstrap <<<\n'; } >> "$BASHRC"
    chown "$REAL_USER:$REAL_USER" "$BASHRC" 2>/dev/null || true
    ok "Shell PATH" "PATH and venv activation added to $BASHRC"
    _bashrc_patched=1
fi

step "Starting 9router"
ROUTER_BIN=$(command -v 9router 2>/dev/null || echo "$NPM_BIN/9router")
_ensure_9router install

step "Installing Gateway Watchdog"
OPENCLAW_BIN=$(command -v openclaw 2>/dev/null || echo "$NPM_BIN/openclaw")
_ensure_gateway_watchdog install

_fix_ownership

step "Removing Useless Files"
_clean_user_side
ok "User Cleanup" "Caches and temporary files removed"

_spin_stop
[[ "${_bashrc_patched:-0}" -eq 1 ]] && note "Reload shell config:  source $BASHRC"
printf "\n  ${C_GREEN}openclaw installed${C_RESET}  ${C_GRAY}(%ds)${C_RESET}\n\n" "$(_elapsed)"
fi

# ═════════════════════════════════════════════════════════════════════════════
# UPDATE MODE
# ═════════════════════════════════════════════════════════════════════════════
if [[ "$MODE" == update ]]; then
_section "$TITLE" "$SUBTITLE"

step "Updating System Packages"
_wait_apt_lock; _apt_fix_broken
run_quiet "apt-get update" apt-get update -qq
run_quiet "Upgrading System Packages" env DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends
ok "System Packages" "All system packages up to date"
apt-get clean; rm -rf /var/lib/apt/lists/*

step "Updating UV"
_old_uv=$(uv_ver)
if as_user "$UV_BIN/uv" self update >> "$LOG_FILE" 2>&1; then
    _new_uv=$(uv_ver)
    [[ "$_old_uv" != "$_new_uv" ]] && ok "UV" "Updated: $_old_uv → $_new_uv" || ok "UV" "$_new_uv (already latest)"
else warn "UV" "Update failed — see $LOG_FILE"; fi

step "Checking Node.js"
_ver=$(node --version 2>/dev/null || echo "v0"); _maj="${_ver#v}"; _maj="${_maj%%.*}"
if [[ "$_maj" -ge "$NODE_MAJOR" ]]; then ok "Node.js" "$_ver"
else warn "Node.js" "Found $_ver — v${NODE_MAJOR}+ required, upgrading"; _install_node; ok "Node.js" "$(node --version) installed"; fi

step "Updating Python Libraries"
if run_quiet "Updating Python Libraries" as_user "$UV_BIN/uv" pip install --no-cache --upgrade --python "$VENV_DIR/bin/python" "${PYTHON_PKGS[@]}"; then
    ok "Python Libraries" "All Python packages up to date"
else
    warn "Python Libraries" "Upgrade encountered errors — see $LOG_FILE"
fi

step "Updating Chromium"
_scrapling_marker=$(find "$VENV_DIR/lib" -maxdepth 4 -name ".scrapling_dependencies_installed" 2>/dev/null | head -1)
if [[ -n "$_scrapling_marker" ]]; then
    ok "Chromium" "Browser up to date"
else
    _wait_apt_lock; _apt_fix_broken
    run_tee --allow-fail "Updating Chromium" as_user env PLAYWRIGHT_BROWSERS_PATH="$PW_CACHE" "$VENV_DIR/bin/playwright" install chromium
    chown -R "$REAL_USER:$REAL_USER" "$PW_CACHE" 2>/dev/null || true
    _touch_scrapling_marker
    ok "Chromium" "Browser updated successfully"
fi

step "Updating NPM Packages"
_outdated=$(npm_g outdated --json 2>/dev/null || true)
chown -R "$REAL_USER:$REAL_USER" "$NPM_PREFIX" 2>/dev/null || true
for _spec in "${NPM_PKGS[@]}"; do
    _pkg=$(strip_npm_pkg "$_spec"); _label="${NPM_PKG_LABELS[$_pkg]:-$_pkg}"
    [[ "$_pkg" == npm ]] && { npm_g install "$_spec" --loglevel=silent >> "$LOG_FILE" 2>&1 || true; continue; }
    if printf '%s\n' "$_outdated" | grep -q "\"${_pkg}\""; then
        _old_ver=$(npm_pkg_ver "$_pkg")
        if npm_g install "$_spec" --loglevel=warn >> "$LOG_FILE" 2>&1; then ok "$_label" "Updated: $_old_ver → $(npm_pkg_ver "$_pkg")"
        else warn "$_label" "Update failed — see $LOG_FILE"; fi
    else ok "$_label" "$(npm_pkg_ver "$_pkg") (already latest)"; fi
done
chown -R "$REAL_USER:$REAL_USER" "$NPM_PREFIX" 2>/dev/null || true

step "Refreshing System Shortcuts"
_apply_symlinks

step "Checking Mcporter"
if command -v mcporter &>/dev/null; then
    as_user mcporter config list 2>/dev/null | grep -q "google-workspace" && ok "Mcporter" "Google Workspace connector active" || { as_user mcporter config add google-workspace --command "npx" --arg "-y" --arg "@presto-ai/google-workspace-mcp" --scope home >> "$LOG_FILE" 2>&1 && ok "Mcporter" "Google Workspace connector registered" || warn "Mcporter" "Connector registration failed — see $LOG_FILE"; }
else warn "Mcporter" "Binary not found — skipping"; fi

step "Restarting 9router"
ROUTER_BIN=$(command -v 9router 2>/dev/null || echo "$NPM_BIN/9router")
_ensure_9router update

step "Reinstalling Gateway Watchdog"
OPENCLAW_BIN=$(command -v openclaw 2>/dev/null || echo "$NPM_BIN/openclaw")
_ensure_gateway_watchdog install

_fix_ownership

step "Removing Useless Files"
_clean_user_side
ok "User Cleanup" "Caches and temporary files removed"

_spin_stop
printf "\n  ${C_GREEN}openclaw updated${C_RESET}  ${C_GRAY}(%ds)${C_RESET}\n\n" "$(_elapsed)"
fi

# ═════════════════════════════════════════════════════════════════════════════
# REPAIR MODE (Deep Clean)
# ═════════════════════════════════════════════════════════════════════════════
if [[ "$MODE" == repair ]]; then
_section "$TITLE" "$SUBTITLE"

step "Cleaning Package Manager State"
run_quiet "Purging APT Cache" env DEBIAN_FRONTEND=noninteractive apt-get autoremove -y --purge
run_quiet "Cleaning APT" sh -c 'apt-get clean && apt-get autoclean'
rm -rf /var/lib/apt/lists/*
ok "Package Manager" "Cache purged and orphaned packages removed"

step "Removing Useless Files"
_clean_user_side
ok "User Cleanup" "Caches, trash, and temporary artifacts removed"

step "Fixing Python Venv"
if [[ -f "$VENV_DIR/bin/activate" ]] && ! as_user "$VENV_DIR/bin/python" --version &>/dev/null; then
    rm -rf "$VENV_DIR"
    if command -v uv &>/dev/null || [[ -x "$UV_BIN/uv" ]]; then
        as_user "$UV_BIN/uv" venv --python "$PYTHON_VER" "$VENV_DIR" >> "$LOG_FILE" 2>&1
        ok "Python Venv" "Environment rebuilt successfully"
        warn "Action Required" "Run 'bash boot.sh' to reinstall Python packages"
    else
        warn "Python Venv" "Cannot rebuild — UV package manager not found"
    fi
else
    ok "Python Venv" "Environment is healthy"
fi

step "Removing Gateway Watchdog"
OPENCLAW_BIN=$(command -v openclaw 2>/dev/null || echo "$NPM_BIN/openclaw")
_ensure_gateway_watchdog remove

step "Reinstalling Gateway Watchdog"
_ensure_gateway_watchdog install

step "Fixing NPM State"
if command -v npm &>/dev/null; then
    for _lock in "$NPM_PREFIX/.package-lock.json" "$NPM_PREFIX/node_modules/.package-lock.json"; do
        [[ -f "$_lock" ]] && rm -f "$_lock"
    done
    ok "NPM State" "Stale lock files removed"
else
    ok "NPM State" "Skipped — npm not installed"
fi

step "Fixing File Ownership"
mkdir -p "$OPENCLAW_WORKSPACE" "$REAL_HOME/.config" "$PW_CACHE"
chown -R "$REAL_USER:$REAL_USER" \
    "$REAL_HOME/.openclaw" \
    "$REAL_HOME/.local" \
    "$REAL_HOME/.config" \
    "$NPM_PREFIX" \
    "$VENV_DIR" \
    "$PW_CACHE" 2>/dev/null || true
chmod -R u+rwX \
    "$REAL_HOME/.openclaw" \
    "$REAL_HOME/.local" \
    "$REAL_HOME/.config" \
    "$NPM_PREFIX" \
    "$VENV_DIR" \
    "$PW_CACHE" 2>/dev/null || true
ok "File Permissions" "Ownership and permissions corrected"

step "Removing Orphaned Chromium"
if [[ -d "$PW_CACHE" ]]; then
    _pw_expected=""; [[ -f "$VENV_DIR/bin/python" ]] && _pw_expected=$(pw_expected_revision)
    while IFS= read -r -d '' _dir; do
        _rev=$(basename "$_dir" | sed 's/chromium-//')
        [[ -n "$_pw_expected" && "$_rev" != "$_pw_expected" ]] && { rm -rf "$_dir"; note "Removed orphaned Chromium build: r$_rev"; }
    done < <(find "$PW_CACHE" -maxdepth 1 -name "chromium-*" -type d -print0 2>/dev/null)
    ok "Chromium" "Orphaned browser builds removed"
else
    ok "Chromium" "Skipped — browser not installed"
fi

_spin_stop
printf "\n  ${C_GREEN}repair complete${C_RESET}  ${C_GRAY}(%ds)${C_RESET}\n\n" "$(_elapsed)"
fi
