# import paramiko
# try:
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(hostname='192.168.73.169', username='root', password='Password1')
#     sftp = ssh.open_sftp()
#     sftp.put(r"C:\demo\28c74d8a-17e7-459d-b14c-e9c00154f57f.tar", '/root/some.tar')
#
# finally:
#     ssh.close()

import logging
from import_files_from_artifactory import populate_build_from_sandbox, mock_reservation
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers

def mock_connectivity():
    global connectivity

    class Object(object):
        pass

    connectivity = Object()
    connectivity.server_address = '192.168.73.152'
    connectivity.admin_user = 'admin'
    connectivity.admin_pass = 'admin'

logging.basicConfig(filename='example.log', level=logging.DEBUG)
reservation = mock_reservation('29e6d90c-eac9-4542-a693-78513d018395', 'Global')
mock_connectivity()
what_i_got = populate_build_from_sandbox(connectivity=connectivity, reservation=reservation, msg=logging.debug)
print what_i_got


