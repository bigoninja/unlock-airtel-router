from zyxel_backup_restore import ZyxelBackupTool

ROUTER_IP = "192.168.1.1"
USERNAME = "admin"
PASSWORD = "<your-router-password>"

confirmation = input("Type RESTORE to apply router config: ")

if confirmation != "RESTORE":
    raise SystemExit("Cancelled")

tool = ZyxelBackupTool(ROUTER_IP)

if not tool.encrypt_config("config-edited.xml", "config-edited.cfg"):
    raise SystemExit("Encryption failed; restore was not attempted")

if not tool.login(USERNAME, PASSWORD):
    raise SystemExit("Login failed")

if not tool.restore_backup("config-edited.cfg"):
    raise SystemExit("Restore failed")

print("Restore request submitted.")
