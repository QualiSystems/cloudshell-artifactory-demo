import requests
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers
import json
import shutil


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
            "archiveType": "zip"
        }

        headers = {'content-type': 'application/json'}
        response = requests.post(artifactory_url, auth=(self.user, self.password), headers=headers, json=data)

        save_artifacts_archive_to = "c:/demo/{0}.zip".format(reservation_id)

        zfile = open(save_artifacts_archive_to, 'wb')
        zfile.write(response.content)
        zfile.close()

        del response
        return save_artifacts_archive_to


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
    app_attributes = helpers.get_resource_context_details().attributes
    connectivity = helpers.get_connectivity_context_details()

    cloudshell = helpers.get_api_session()

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

    file_location = artifactory.download(build.name, build.number, reservation.id)

    print '- Downloaded app dependencies to ' + file_location





if __name__ == "__main__":
    main()