import requests
import sys
from uuid import UUID
import os.path


def main():
    if len(sys.argv) < 4:
        raise Exception('must pass in reservation_id, archive filepath and cloudshell server host')

    try:
        ReservationID = UUID(sys.argv[1], version=4)
    except Exception as e:
        raise Exception('first argument was not a reservation id')

    artifactory_metadata_file_path = sys.argv[2]
    server_address = sys.argv[3]

    if not os.path.isfile(artifactory_metadata_file_path):
        raise Exception('second argument is file path, but file does not exist')

    quali_api_port = '9000'
    user = 'admin'
    password = 'admin'
    domain = 'Global'
    creds = {"username": user, "password": password, "domain": domain}

    # Login to Quali API
    login_result = requests.put('http://{0}:{1}/Api/Auth/Login'.format(server_address, quali_api_port), creds)
    authcode = "Basic " + login_result.content[1:-1]

    with open(artifactory_metadata_file_path, 'rb') as upload_file:
        res = requests.post('http://{0}:{1}/API/Package/AttachFileToReservation'.format(server_address,
                                                                                        quali_api_port),
                            headers={"Authorization": authcode},
                            data={"reservationId": ReservationID, "saveFileAs": "artifactory-metadata",
                                  "overwriteIfExists": "True"},
                            files={'QualiPackage': upload_file})


if __name__ == "__main__":
    main()
