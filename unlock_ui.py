"""
============================================
Unlock the web UI now and after reboot.
============================================

PREREQUISITES:
    - Requires a working router SSH connection.
    - Run `python enable_ssh.py` to enable SSH on the router.
"""

import subprocess

from zyxel_backup_restore import get_router_credentials

REQUEST = """RDMNAME config;
REQUEST;
SEL InternetGatewayDevice.DeviceInfo;
SET X_5067F0_DebugVersionFlag boolean 1;
SEND;
REQUEST;
SEL InternetGatewayDevice.DeviceInfo;
GET X_5067F0_DebugVersionFlag;
SEND;
"""

UNLOCK = f"""reply=$(/usr/bin/ccctest -f /proc/self/fd/0 2>&1 <<'UNLOCK_CCC'
{REQUEST}UNLOCK_CCC
)
printf '%s\\n' "$reply"
case "$reply" in
    *"GET X_5067F0_DebugVersionFlag: success"*"Value=1"*)
        echo 'UI flag enabled.' ;;
    *)
        echo 'Could not confirm the UI flag.' >&2
        exit 1 ;;
esac
"""

SCRIPT = f"""set -e
umask 077

{UNLOCK}
startup=/etc/rc.local
if [ ! -f "$startup" ]; then
    printf '#!/bin/sh\\n\\nexit 0\\n' > "$startup"
fi
if grep -Fxq '# BEGIN_UNLOCK_UI' "$startup" ||
   grep -Fxq 'SET X_5067F0_DebugVersionFlag boolean 1;' "$startup"; then
    echo 'UI startup command is already installed.'
    exit 0
fi

case "$(head -n 1 "$startup")" in
    '#!'*) ;;
    *) echo 'rc.local must start with a shell shebang.' >&2; exit 1 ;;
esac

block=$(mktemp)
candidate=$(mktemp /etc/rc.local.XXXXXX)
trap 'rm -f "$block" "$candidate"' 0
cat > "$block" <<'UNLOCK_STARTUP'
# BEGIN_UNLOCK_UI
(
    sleep 90
{UNLOCK}
) </dev/null > /tmp/unlock-ui.log 2>&1 &
# END_UNLOCK_UI
UNLOCK_STARTUP

cp -p "$startup" "$candidate"
sed "1r $block" "$startup" > "$candidate"
sh -n "$candidate"
mv -f "$candidate" "$startup"
echo 'UI startup script installed.'
"""


def main():
    router_ip, username, _ = get_router_credentials(require_password=False)
    subprocess.run([
        "ssh",
        "-o", "HostKeyAlgorithms=+ssh-rsa",
        "-o", "PreferredAuthentications=password",
        "-o", "PasswordAuthentication=yes",
        "-o", "PubkeyAuthentication=no",
        f"{username}@{router_ip}", SCRIPT,
    ], check=True)
    print("Refresh the router page to see the unlocked controls.")
    print("Wait ~2-3 minutes after rebooting router to make sure script is correctly executed.")


if __name__ == "__main__":
    main()
