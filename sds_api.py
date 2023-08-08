import datetime
import json
import os

import requests

# CONFIGURATION

# Enter in the URL of the API that we're testing.
API_URL = ""  # ex - "https://api.prod.imap-mission.com"

# When an authentication system is set up, these must be set to log in to the APIs
AWS_REGION = ""  # ex - "us-west-2"
COGNITO_CLIENT_ID = ""  # random string of letters assigned to the congito client

# GLOBAL VARIABLES

# These variables are set when a user is logged in.
USER_TOKEN = None
LOGIN_TIME = None

# These variables are never changed
EXPIRE_TIME = 3600
STATUS_OK = 200
STATUS_NOT_FOUND = 404
STATUS_BAD_REQUEST = 400


def _set_user_token(t):
    global LOGIN_TIME
    global USER_TOKEN

    LOGIN_TIME = datetime.datetime.now()
    USER_TOKEN = t


def _get_user_token():
    if LOGIN_TIME is None:
        print("New login needed.  Login is valid for 60 minutes.")
    elif (datetime.datetime.now() - LOGIN_TIME).total_seconds() >= EXPIRE_TIME:
        print("Login expired.  Please log in again.")
    else:
        return USER_TOKEN

    t = get_sdc_token()

    return t


def get_sdc_token(user_name=None, password=None):
    """
    This function authenticates the user.  An access token is automatically stored in
    the USER_TOKEN variable in this file, and functions will attempt to find a valid
    user token in that variable.

    :param user_name: User's SDC username
    :param password: User's SDC password

    :return: A string that also gets stored in the USER_TOKEN variable in this file.
             You don't need this string unless you plan on making your own API calls,
             using functions outside of this file.
    """

    if user_name is None:
        user_name = input("Username:")
    if password is None:
        import getpass

        password = getpass.getpass("Password for " + user_name + ":")

    authentication_url = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/"
    authentication_headers = {
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
        "Content-Type": "application/x-amz-json-1.1",
    }
    data = json.dumps(
        {
            "ClientId": COGNITO_CLIENT_ID,
            "AuthFlow": "USER_PASSWORD_AUTH",
            "AuthParameters": {"USERNAME": user_name, "PASSWORD": password},
        }
    )

    # Attempt to grab the SDC token.
    try:
        token_response = requests.post(
            authentication_url, data=data, headers=authentication_headers
        )
        t = token_response.json()["AuthenticationResult"]["AccessToken"]
    except KeyError:
        print("Invalid username and/or password.  Please try again.  ")
        return

    _set_user_token(t)

    return t


def _execute_api_get(endpoint, login, **kwargs):
    if login:
        token = _get_user_token()
        headers = {"Authorization": token}
    else:
        headers = {}
    query_parameters = []
    for kw in kwargs:
        query_parameters.append(kw + "=" + str(kwargs[kw]))
    query_parameters = "&".join(query_parameters)
    url_with_parameters = API_URL + "/" + endpoint + "?" + query_parameters
    print(url_with_parameters)
    try:
        response = requests.get(url_with_parameters, headers=headers)
    except Exception as e:
        print(f"Could not finish query due to error {e!s}")
        return
    return response


def download(filename, download_dir=".", login=False):
    """
    This function is used to download files from the SDS.

    :param filename: The full S3 URI to download
    :param download_dir: The directory on the local machine to download the file to.

    :return: None, but downloads the file to the specified download directory
    """
    endpoint = "download"
    download_url = _execute_api_get(endpoint, login, s3_uri=filename)

    if download_url.status_code == STATUS_BAD_REQUEST:
        print("Not a valid S3 URI.  Example input: s3://bucket/path/file.ext")
        return
    elif download_url.status_code == STATUS_NOT_FOUND:
        print("No files were found matching the given URI.")
        return

    file_name_and_path = os.path.join(download_dir, filename[5:])
    download_dir = os.path.dirname(file_name_and_path)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    with open(file_name_and_path, "wb") as file:
        print(f"Downloading {file_name_and_path}")
        file_location = requests.get(download_url.json()["download_url"])
        file.write(file_location.content)

    return file_name_and_path


def query(login=False, **kwargs):
    """
    This function is used to query files from the SDS.
    There are no required arguments, the search strings will depend on the mission

    :return: This returns JSON with all information about the files.
    """
    endpoint = "query"
    response = _execute_api_get(endpoint, login, **kwargs)
    return response.json()


def upload(local_file_location, remote_file_name, login=False, **kwargs):
    """
    This function is used to upload files to the SDS.

    :param local_file_location: The full filename and path to the file on the
                                local machine to upload to the SDS.
    :param remote_file_name: The name of the file you'd like the uploaded file to be
    :param kwargs: Any additional key word arguments passed into this function
                   are stored as tags on the SDS.

    :return: This returns a requests response object.
             If the upload was successful, it'll be code 200.
    """
    endpoint = "upload"
    response = _execute_api_get(endpoint, login, filename=remote_file_name, **kwargs)

    if response.status_code != STATUS_OK:
        print(
            "Could not generate an upload URL with the following error: "
            + response.text
        )
        return

    with open(local_file_location, "rb") as object_file:
        object_text = object_file.read()

    response = requests.put(response.json(), data=object_text)
    return response
