"""
============================================
Download and decrypt the router config
============================================
"""

from zyxel_backup_restore import ZyxelBackupTool, get_router_credentials


def main():
    router_ip, username, password = get_router_credentials()

    tool = ZyxelBackupTool(router_ip)

    if not tool.login(username, password):
        raise SystemExit("Login failed")

    if not tool.download_backup("config-current.cfg"):
        raise SystemExit("Backup failed")

    if not tool.decrypt_backup("config-current.cfg", "config-current.xml"):
        raise SystemExit("Backup downloaded, but decryption failed")

    print("Backup downloaded to config-current.cfg and decrypted to config-current.xml.")


if __name__ == "__main__":
    main()
