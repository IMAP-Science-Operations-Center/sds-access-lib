# SDS-access-lib

This is a simple python script that allows a user to upload, query, and download data from a a Science Data System as set up from: https://github.com/IMAP-Science-Operations-Center/sds-data-manager

## Uploading Data Example

```
>>> import sds_api
>>> response = sds_api.upload(file_location='helloworld.txt', file_name='imap_l0_sci_mag_2024_2_ThisWillMakeThingsFail.pkts')
Could not generate an upload URL with the following error: "A pre-signed URL could not be generated. Please ensure that the file name matches mission file naming conventions."
>>> response = sds_api.upload(file_location='helloworld.txt', file_name='imap_l0_sci_mag_2024_2.pkts')
```

## Querying Data Example
```
>>> results = sds_api.query(instrument='imap-lo')
>>> print(results)
[]
>>> results = sds_api.query(instrument='mag')
>>> print(results)
[{'_index': 'metadata', '_type': '_doc', '_source': {'date': '2024', 'mission': 'imap', 'extension': 'pkts', 'level': 'l0', 'instrument': 'mag', 'type': 'sci', 'version': '2'}, '_id': 's3://sds-data-harter-upload-testing/imap/l0/imap_l0_sci_mag_2024_2.pkts', '_score': 0.18232156}, {'_index': 'metadata', '_type': '_doc', '_source': {'date': '2024', 'mission': 'imap', 'extension': 'pkts', 'level': 'l0', 'instrument': 'mag', 'type': 'sci', 'version': ''}, '_id': 's3://sds-data-harter-upload-testing/imap/l0/imap_l0_sci_mag_2024_.pkts', '_score': 0.18232156}]
```

## Downloading Data Example
```
>>> response = sds_api.download(results[0]['_id'])
Downloading sds-data-harter-upload-testing/imap/l0/imap_l0_sci_mag_2024_2.pkts
```