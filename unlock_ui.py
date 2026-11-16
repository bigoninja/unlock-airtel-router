"""
============================================
Unlock the web UI now and after reboot.
============================================
"""

import subprocess

from zyxel_backup_restore import get_router_credentials

REQUEST_UINT8 = """RDMNAME config;
REQUEST;
SEL InternetGatewayDevice.DeviceInfo;
SET X_5067F0_DebugVersionFlag uint8 1;
SEND;
REQUEST;
SEL InternetGatewayDevice.DeviceInfo;
GET X_5067F0_DebugVersionFlag;
SEND;
"""

REQUEST_BOOL = """RDMNAME config;
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
{REQUEST_UINT8}UNLOCK_CCC
) || :
if ! printf '%s\\n' "$reply" | grep -q 'GET X_5067F0_DebugVersionFlag: success' ||
   ! printf '%s\\n' "$reply" | grep -q '^[[:space:]]*Value=1[[:space:]]*$'; then
    reply=$(/usr/bin/ccctest -f /proc/self/fd/0 2>&1 <<'UNLOCK_CCC'
{REQUEST_BOOL}UNLOCK_CCC
    ) || :
fi
printf '%s\\n' "$reply"
if printf '%s\\n' "$reply" | grep -q 'GET X_5067F0_DebugVersionFlag: success' &&
   printf '%s\\n' "$reply" | grep -q '^[[:space:]]*Value=1[[:space:]]*$'; then
    echo 'UI flag enabled.'
else
    echo 'Could not confirm the UI flag.' >&2
    exit 1
fi
"""

SCRIPT = f"""set -e
umask 077

{UNLOCK}
startup=/etc/rc.local
if [ ! -f "$startup" ]; then
    printf '#!/bin/sh\\n\\nexit 0\\n' > "$startup"
fi
if grep -Fxq '# BEGIN_UNLOCK_UI' "$startup" ||
   grep -q 'SET X_5067F0_DebugVersionFlag' "$startup"; then
    echo 'UI startup command is already installed.'
    exit 0
fi

block="/tmp/unlock_block_$$.tmp"
candidate="/tmp/rc.local_$$.tmp"
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

case "$(head -n 1 "$startup")" in
    '#!'*)
        sed "1r $block" "$startup" > "$candidate"
        ;;
    *)
        {{
            printf '#!/bin/sh\\n'
            cat "$block"
            cat "$startup"
        }} > "$candidate"
        ;;
esac

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
    print("After future reboots, give the router ~2-3 minutes for the UI unlock script to run.")

if __name__ == "__main__":
    main()
