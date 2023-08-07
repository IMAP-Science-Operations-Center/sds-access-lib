import pytest
import requests
import sds_api

def test_query(requests_mock):
    # Set up the fake API endpoint
    sds_api.API_URL ='https://imap_sds_api.com'
    requests_mock.get('https://imap_sds_api.com/query', json={"file": "imap.csv"})
    
    # Query and ensure a match
    assert {"file": "imap.csv"} == sds_api.query(login=False)

def test_download_success(requests_mock):
    # Set up the fake API endpoints
    sds_api.API_URL ='https://imap_sds_api.com'
    fake_file_contents = "Hello World!"
    requests_mock.get('https://imap_sds_api.com/download', json={"download_url": "https://big-s3-signed-url.com"}, status_code='200')
    requests_mock.get('https://big-s3-signed-url.com', content=b"Hello World!")

    # Download a file with the name "imap.txt", and contents of "Hello World!"
    file_location = sds_api.download("s3://imap.txt", login=False)

    assert file_location == "./imap.txt"

    # Download a file 
    with open(file_location) as f:
        contents = f.read()

    assert contents == "Hello World!"

def test_download_fail(requests_mock):
    # Set up the fake API endpoints
    sds_api.API_URL ='https://imap_sds_api.com'
    fake_file_contents = "Hello World!"
    requests_mock.get('https://imap_sds_api.com/download', json={"download_url": "https://big-s3-signed-url.com"}, status_code=400)
    requests_mock.get('https://big-s3-signed-url.com', content=b"Hello World!")

    # Download a file with the name "imap.txt", and contents of "Hello World!"
    file_location = sds_api.download("s3://imap.txt", login=False)

    assert file_location == None