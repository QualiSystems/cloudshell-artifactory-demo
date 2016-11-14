import requests
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers
import json
import paramiko
import os


def scp_copy(host, user, password, local_path, remote_path):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname=host, username=user, password=password, timeout=300)
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()



class ArtifactBuild:
    def __init__(self, name, number):
        self._name = name
        self._number = number

    def __init__(self, data):
        self._name = data["Build Name"]
        self._number = data["Build Number"]

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number

    def is_populated(self):
        return self.name != '' and self.number != ''


class Artifactory:
    def __init__(self, host, port, user, password):
        self._host = host
        self._port = port
        self._user = user
        self._password = password

    def __init__(self, repo_details):
        self._host = repo_details["Host"]
        self._port = repo_details["Port"]
        self._user = repo_details["User"]
        self._password = repo_details["Password"]

    @property
    def host (self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    def download(self, buildName, buildNumber, reservation_id):
        artifactory_url = "http://{0}:{1}/artifactory/api/archive/buildArtifacts".format(self.host, self.port)
        data = {
            "buildName": buildName.encode(),
            "buildNumber": buildNumber.encode(),
            "archiveType": "tar"
        }

        headers = {'content-type': 'application/json'}
        response = requests.post(artifactory_url, auth=(self.user, self.password), headers=headers, json=data)

        file_name = "binaries_for_{0}_{1}.tar".format(buildName,buildNumber)
        save_artifacts_archive_to = "c:\\demo"

        zfile = open(os.path.join(save_artifacts_archive_to, file_name), 'wb')
        zfile.write(response.content)
        zfile.close()

        del response
        return save_artifacts_archive_to, file_name


def mock_reservation():
    global reservation

    class Object(object):
        pass

    reservation = Object()
    reservation.id = '115b6d9f-f736-4682-bbc5-eba535520568'

def populate_build_from_sandbox(build, connectivity, reservation):
    serveraddress = connectivity.server_address
    quali_api_port = '9000'
    user = connectivity.admin_user
    password = connectivity.admin_pass
    domain = reservation.domain
    print '- Checking if sandbox associated with a build'
    creds = {"username": user, "password": password, "domain": domain}
    login_result = requests.put('http://{0}:{1}/Api/Auth/Login'.format(serveraddress, quali_api_port), creds)
    authcode = "Basic " + login_result.content[1:-1]
    response = requests.post(
        "http://{0}:{1}/API/Package/GetReservationAttachment".format(serveraddress, quali_api_port),
        headers={"Authorization": authcode},
        data={"reservationId": reservation.id,
              "Filename": "artifactory-metadata"})
    try:
        metadata = json.loads(response.text.replace('/r/n', ''))
    except Exception:
        print '- App not associated with a build'
    print '- found a build with artifacts hosted on Artifactory: {0} {1}'.format(metadata['buildName'],
                                                                                 metadata['buildNumber'])
    build = ArtifactBuild(metadata['buildName'], metadata['buildNumber'])
    return build

def main():
    reservation = helpers.get_reservation_context_details()
    app = helpers.get_resource_context_details()
    app_attributes = app.attributes
    connectivity = helpers.get_connectivity_context_details()
    cloudshell = helpers.get_api_session()


    resource = helpers.get_resource_context_details_dict()
    resource['deployedAppData']['attributes'] = {attribute['name']: attribute['value'] for attribute in resource['deployedAppData']['attributes']}
    resource['deployedAppData']['attributes']['Password'] = cloudshell.DecryptPassword(resource['deployedAppData']['attributes']['Password']).Value

    repo = cloudshell.GetResourceDetails(app_attributes["Artifactory Name"])
    repo_attributes = {attribute.Name:attribute.Value for attribute in repo.ResourceAttributes}
    repo_attributes["Host"] = repo.Address
    # mock_reservation()

    artifactory = Artifactory(repo_attributes)
    build = ArtifactBuild(repo_attributes)

    print '- Looking for app dependencies'

    if not build.is_populated():
        build = populate_build_from_sandbox(build, connectivity, reservation)

    print '- Found dependencies on Artifactory, associated with build {0} {1}'.format(build.name, build.number)

    file_location, file_name = artifactory.download(build.name, build.number, reservation.id)

    print '- Downloaded app dependencies to ' + os.path.join(file_location, file_name)

    scp_copy(resource['deployedAppData']['address'], resource['deployedAppData']['attributes']['User'], resource['deployedAppData']['attributes']['Password'],
             os.path.join(file_location, file_name), app_attributes['Target Directory'] + '/' + file_name)





if __name__ == "__main__":
    main()