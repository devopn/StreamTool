from socket import timeout
import paramiko
from .config import ConfigTool 
class SshTool:
    def __init__(self) -> None:
        self._ssh_client = paramiko.SSHClient()
        self.isStarted = False

    def start(self):
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cred = ConfigTool.read()
        if not cred:
            raise Exception("No credentials found")
        if not cred.get("address") or not cred.get("login") or not cred.get("password"):
            raise Exception("Invalid credentials")
        self._ssh_client.connect(cred["address"], port=22, username=cred["login"], password=cred["password"])
        if not self._ssh_client.get_transport().is_active():
            raise Exception("Connection failed")
        self.isStarted = True

    def execute(self, command: str) -> str:
        if not self.isStarted:
            return ""
        print(command)
        stdin, stdout, stderr = self._ssh_client.exec_command(command)
        return stdout.read().decode("utf-8")
    
    def create_stream(self, filename: str, time: str,duration: int, key: str) -> str:
        if not self.isStarted:
            return ""
        result = self.execute(
            f"echo 'screen -d -m -S stream_{filename[:15]}_{time.replace(' ', '_')} timeout {duration*60} ffmpeg -re -i /var/stream/{filename} -c copy -f flv {key}' | at {time}"
            )
        return result
    
    def kill_stream(self, stream_id: str) -> str:
        if not self.isStarted:
            return ""
        result = self.execute(f"screen -XS {stream_id} quit")
        return result
    
    def list_streams(self) -> str:
        if not self.isStarted:
            return ""
        result = self.execute("screen -ls")
        return result
    
    def get_streams(self, date: str) -> str:
        if not self.isStarted:
            return ""
        result = self.execute(f'atq -o "%d-%m-%Y %H:%M:%S" | grep {date}')
        return result
    
    def delete_stream(self, date: str) -> str:
        if not self.isStarted:
            return ""
        result = self.execute(f'atq -o "%d-%m-%Y %H:%M:%S" | grep {date}')
        for i in result.split("\n"):
            a = i.split()
            if a:
                self.execute(f'atrm {a[0]}')
    def stop(self):
        self._ssh_client.close()

    