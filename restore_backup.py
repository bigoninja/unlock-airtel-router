"""
============================================
Encrypt and restore config
============================================
"""

from zyxel_backup_restore import ZyxelBackupTool, get_router_credentials


def main():
    confirmation = input("Type RESTORE to apply router config: ")

    if confirmation != "RESTORE":
        raise SystemExit("Cancelled")

    router_ip, username, password = get_router_credentials()

    tool = ZyxelBackupTool(router_ip)

    if not tool.encrypt_config("config-edited.xml", "config-edited.cfg"):
        raise SystemExit("Encryption failed; restore was not attempted")

    if not tool.login(username, password):
        raise SystemExit("Login failed")

    if not tool.restore_backup("config-edited.cfg"):
        raise SystemExit("Restore failed")

    print("Restore request submitted.")


if __name__ == "__main__":
    main()
