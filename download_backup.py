from zyxel_backup_restore import ZyxelBackupTool

ROUTER_IP = "192.168.1.1"
USERNAME = "admin"
PASSWORD = "<your-router-password>"

tool = ZyxelBackupTool(ROUTER_IP)

if not tool.login(USERNAME, PASSWORD):
    raise SystemExit("Login failed")

if not tool.download_backup("backup-current.cfg"):
    raise SystemExit("Backup failed")

if not tool.decrypt_backup("backup-current.cfg", "backup-current.xml"):
    raise SystemExit("Backup downloaded, but decryption failed")

print("Backup downloaded to backup-current.cfg and decrypted to backup-current.xml.")
