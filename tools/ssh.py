from socket import timeout
import paramiko
from .config import ConfigTool 
class SshTool:
    def __init__(self) -> None:
        self._ssh_client = paramiko.SSHClient()

    def start(self):
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cred = ConfigTool.read()
        if not cred:
            raise Exception("No credentials found")
        if not cred.get("address") or not cred.get("login") or not cred.get("password"):
            raise Exception("Invalid credentials")
        self._ssh_client.connect(cred["address"], port=22, username=cred["login"], password=cred["password"])

    def execute(self, command: str) -> str:
        print(command)
        stdin, stdout, stderr = self._ssh_client.exec_command(command)
        return stdout.read().decode("utf-8")
    
    def create_stream(self, filename: str, time: str,duration: int, key: str) -> str:
        result = self.execute(
            f"echo 'screen -d -m -S stream_{filename[:15]}_{time} timeout {duration} ffmpeg -re -i /var/stream{filename} -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{key}' | at {time}"
            )
        return result
    
    def kill_stream(self, stream_name: str) -> str:
        result = self.execute(f"screen -S {stream_name} -X quit")
        return result
    
    def delete_stream(self, date: str) -> str:
        pass
    def stop(self):
        self._ssh_client.close()

    