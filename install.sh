#!/bin/sh
# Procedural Prompting -- the installer for Linux and macOS.
#
#   sh install.sh [--house <folder>] [--harness claude|codex|gemini|cursor] [--packages "<names>"] [--no-launch]
#   curl -LsSf https://raw.githubusercontent.com/VogtVan/pp/main/install.sh | sh
#
# In order: uv, installed when it is missing; the product -- the folder this script stands
# in, or, when it is piped, the archive of `main` extracted as `./pp`; the house, installed
# beside the product, or brought up to date when it stands (`pp upgrade --from`, nothing
# else); the post's launcher `pp-ui` (`pp-ui-<name>` for a house not named house) beside it; the post, opened. Played again, it
# changes nothing a house holds but what `pp upgrade` moves.
#
#   PP_UV_INSTALLER   uv's installer, a URL or a file   (https://astral.sh/uv/install.sh)
#   PP_ARCHIVE        the product's archive, a URL or a file   (the archive of `main`)
set -eu

USAGE='usage: sh install.sh [--house <folder>] [--harness claude|codex|gemini|cursor] [--packages "<names>"] [--no-launch]'
UV_INSTALLER=${PP_UV_INSTALLER:-https://astral.sh/uv/install.sh}
ARCHIVE=${PP_ARCHIVE:-https://github.com/VogtVan/pp/archive/refs/heads/main.zip}
HOUSE=
HARNESS=claude
PACKAGES='agent team ui'
CHOSEN=
LAUNCH=1

say() { printf 'pp-install: %s\n' "$*"; }
fail() { printf 'pp-install: %s\n' "$*" >&2; exit 2; }

while [ $# -gt 0 ]; do
    case $1 in
        --house) [ $# -ge 2 ] || fail "--house needs a folder"; HOUSE=$2; shift 2 ;;
        --harness)
            [ $# -ge 2 ] || fail "--harness needs a name"
            case $2 in claude|codex|gemini|cursor) HARNESS=$2 ;; *) fail "--harness: claude, codex, gemini or cursor" ;; esac
            CHOSEN=1; shift 2 ;;
        --packages) [ $# -ge 2 ] || fail "--packages needs names"; PACKAGES=$2; CHOSEN=1; shift 2 ;;
        --no-launch) LAUNCH=; shift ;;
        -h|--help) printf '%s\n' "$USAGE"; exit 0 ;;
        *) fail "unknown option '$1' -- $USAGE" ;;
    esac
done

fetch() {    # <URL or file> <destination>
    case $1 in
        http://*|https://*)
            if command -v curl >/dev/null 2>&1; then curl -LsSf "$1" -o "$2"
            elif command -v wget >/dev/null 2>&1; then wget -qO "$2" "$1"
            else fail "neither curl nor wget can fetch $1"
            fi ;;
        *) cp "$1" "$2" ;;
    esac
}

# 1. uv -- installed when missing, then found in this process's PATH
if ! command -v uv >/dev/null 2>&1; then
    say "uv is missing: installing it"
    got=$(mktemp)
    fetch "$UV_INSTALLER" "$got"
    sh "$got"
    rm -f "$got"
    PATH="$HOME/.local/bin:$PATH"
    export PATH
    command -v uv >/dev/null 2>&1 || fail "uv was installed but ~/.local/bin does not hold it"
    say "uv installed -- a new terminal finds it by itself"
fi

# 2. the product -- this script's folder, or the archive extracted as ./pp
here=$(dirname -- "$0")
if [ -f "$here/engine/pp.py" ]; then
    SOURCE=$(cd -- "$here" && pwd)
    ARCHIVED=
else
    SOURCE="$(pwd)/pp"
    ARCHIVED=1
fi
[ -n "$HOUSE" ] || HOUSE="$(dirname -- "$SOURCE")/house"
case $HOUSE in /*) ;; *) HOUSE="$(pwd)/$HOUSE" ;; esac
if [ -n "$ARCHIVED" ]; then
    case $HOUSE/ in "$SOURCE"/*) fail "the house $HOUSE stands inside $SOURCE, which the archive replaces" ;; esac
    if [ -d "$SOURCE/.git" ]; then
        say "$SOURCE is a git clone: left as it is ('git pull' brings it up to date)"
    else
        work=$(mktemp -d)
        fetch "$ARCHIVE" "$work/pp.zip"
        uv run --no-project --quiet python -m zipfile -e "$work/pp.zip" "$work/out"
        top=$(ls "$work/out")
        [ -f "$work/out/$top/engine/pp.py" ] || fail "the archive $ARCHIVE holds no product"
        rm -rf "$SOURCE"
        mv "$work/out/$top" "$SOURCE"
        rm -rf "$work"
        say "the product extracted in $SOURCE"
    fi
fi

# 3. the house -- installed when absent, brought up to date when it stands
if [ -d "$HOUSE/.pp" ]; then
    say "the house $HOUSE stands: bringing it up to date"
    [ -z "$CHOSEN" ] || say "a standing house keeps its packages and its harness ('./pp add <package>' adds one)"
    "$HOUSE/pp" upgrade --from "$SOURCE"
else
    say "installing the house $HOUSE"
    # shellcheck disable=SC2086  # the package names are words on purpose
    uv run "$SOURCE/engine/pp.py" -install "$HOUSE" $PACKAGES "-$HARNESS"
    # 4. the harness -- its command told when missing, never installed
    binary=$(sed -n 's/^BINARY = "\([^"]*\)".*/\1/p' "$SOURCE/adapters/$HARNESS/wire.py")
    [ -z "$binary" ] || command -v "$binary" >/dev/null 2>&1 \
        || say "'$binary' is not on the PATH: install $HARNESS's command line before the first exchange"
fi

# 5. the post's launcher, beside the house, when the house carries the post
place=$(dirname -- "$HOUSE")
name=$(basename -- "$HOUSE")
launcher=pp-ui
[ "$name" = house ] || launcher="pp-ui-$name"    # each house of a folder its own launcher
if "$HOUSE/pp" version -json | grep -q '"ui":'; then
    cat > "$place/$launcher" <<EOF
#!/bin/sh
# Opens the post of the house '$name' beside this file -- written by pp's installer at each of its plays.
exec "\$(cd -- "\$(dirname -- "\$0")" && pwd)/$name/pp" ui "\$@"
EOF
    chmod +x "$place/$launcher"
    printf '@echo off\r\nrem Opens the post of the house %s beside this file -- written by pp'"'"'s installer at each of its plays.\r\ncall "%%~dp0%s\\pp.cmd" ui %%*\r\n' "$name" "$name" > "$place/$launcher.cmd"
    say "the post opens with $place/$launcher"
    # 6. the post, on the terminal this script was started from
    if [ -n "$LAUNCH" ] && [ -t 1 ] && (exec </dev/tty) 2>/dev/null; then
        exec "$HOUSE/pp" ui </dev/tty
    fi
else
    say "the house carries no post: './pp add ui' brings it"
fi
