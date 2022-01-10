from .. utils import err

try:
    from paramiko.client import SSHClient
except ImportError:
    err('paramiko is required for SCP functionality. '
        'Run "pip install paramiko".')

from collections import namedtuple
import re
import getpass

ScpInfo = namedtuple('ScpInfo', 'username host path')

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
        print('Connecting to SSH...')
        passwd = getpass.getpass('Please enter password for {}@{}\n'.format(self._info.username, self._info.host))
        self._client.connect(self._info.host, username=self._info.username, password=passwd)
        self._sftp = self._client.open_sftp()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._sftp.close()
        self._client.close()
        return False

    def send_file(self, remote_file, source_path):
        """
        Upload @source_path to @remote_file
        """
        print('Sending {} --> {}'.format(source_path, self._info.path + '/' + remote_file))
        self._sftp.put(source_path, self._info.path + '/' + remote_file)

def open_client(scp_str):
    return ScpClient(scp_str)
