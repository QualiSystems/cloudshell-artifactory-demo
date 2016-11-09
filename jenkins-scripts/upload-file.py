import requests
import sys
from uuid import UUID

if len(sys.argv) == 1:
    raise Exception('must pass in reservation_id')

try:
    ReservationID = UUID(sys.argv[1], version=4)
except Exception as e:
    raise Exception('first argument was not a reservation id')


serverAddress = 'localhost'
quali_api_port = '9000'
user = 'admin'
password = 'admin'
domain = 'Global'
creds = {"username": user, "password": password, "domain": domain}

# Login to Quali API
login_result = requests.put('http://{0}:{1}/Api/Auth/Login'.format(serverAddress, quali_api_port), creds)
authcode = "Basic " + login_result.content[1:-1]

with open("c:\\debug.txt", 'rb') as upload_file:
    res = requests.post('http://{0}:{1}/API/Package/AttachFileToReservation'.format(serverAddress,
                                                                                    quali_api_port),
                        headers={"Authorization": authcode},
                        data={"reservationId": ReservationID, "saveFileAs": "Build_Detail.pdf",
                              "overwriteIfExists": "True"},
                        files={'QualiPackage': upload_file})
