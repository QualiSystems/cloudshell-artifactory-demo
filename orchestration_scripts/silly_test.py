import paramiko
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='192.168.73.169', username='root', password='Password1')
    sftp = ssh.open_sftp()
    sftp.put(r"C:\demo\28c74d8a-17e7-459d-b14c-e9c00154f57f.tar", '/root/some.tar')

finally:
    ssh.close()
