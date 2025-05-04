import requests
import base64

r = requests.get("https://cloud-palette-dev-storage.s3.amazonaws.com/myNewFile", stream=False)
print(r.status_code)
print(r.headers)
d = r.content
#decoded = base64.decodebytes(d)

op('temp').loadByteArray(d)


