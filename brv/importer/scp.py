import paramiko.client.SSHClient
from collections import namedtuple
import re

ScpInfo = namedtuple('ScpInfo', 'username', 'host', 'path')

def _parse_scp(scp_str):
    """
    scp_str is expected to be in format: user@hostname:/path/
    """
    match = re.match(r'([^@]+)@([^:]+):(.*)', scp_str)

    return ScpInfo(match.group(1), match.group(2), match.group(3))
    

class ScpClient:
    def __init__(self, scp_str):
        self._info = _parse_scp(scp_str)
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.connect(self._info.host, username=self._info.username)
        self._sftp = self._client.open_sftp()

    def __enter__(self):
        pass

    def __exit__(self):
        self._sftp.close()
        self._client.close()

    def send_file(remote_file, source_file):
        """
        Upload @source_path to @remote_file
        """
        with open(source_path, 'rb') as fSource:
            with sftp.file(self._info.path + '/' + remote_file, 'wb') as fTarget:
                while True:
                    copy_buffer = fSource.read(4096)
                    if not copy_buffer:
                        break
                    fTarget.write(copy_buffer)

def open_client(scp_str):
    return ScpClient(scp_str)
