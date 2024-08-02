import paramiko
from .config import ConfigTool 
class SshTool:

    @staticmethod
    def execute(command: str) -> str:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cred = ConfigTool.read()
        if not cred:
            raise Exception("No credentials found")
        if not cred.get("address") or not cred.get("login") or not cred.get("password"):
            raise Exception("Invalid credentials")
        ssh.connect(cred["address"], port=22, username=cred["login"], password=cred["password"])
        stdin, stdout, stderr = ssh.exec_command(command)
        ssh.close()
        return stdout.read()