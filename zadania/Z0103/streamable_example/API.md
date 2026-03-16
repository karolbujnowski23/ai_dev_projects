# Authentication & Security

Authentication is a vital part in protecting your app from malicious usage. In this section we'll go over how to protect different parts of the UploadThing flow.

WARNING: Do not protect the entire `/api/uploadthing` route from being called by unauthenticated users. The endpoint is called as a webhook by our server and thus must be publicly available.

## [Protecting the endpoint from spoofing](https://docs.uploadthing.com/concepts/auth-security#protecting-the-endpoint-from-spoofing)

The callback request is like a webhook that is called by UploadThing when your file has been uploaded to the storage provider. The callback data is signed (HMAC SHA256) using the API key that uploaded the file. Since `v6.7` of the Uploadthing SDK, the callback data is automatically verified before executing the callback. There is no additional work needed to protect the callback endpoint other than making sure you're on a version `^6.7` to ensure your endpoint is appropriately protected.

## [Protecting unauthenticated users from uploading files](https://docs.uploadthing.com/concepts/auth-security#protecting-unauthenticated-users-from-uploading-files)

You can protect unauthenticated users from uploading files via the [`.middleware()`](https://docs.uploadthing.com/file-routes#middleware) function in each file route. This makes it trivial to protect some file routes, and keep some public.

Using your favorite authentication provider (or self-roll if that's your thing), retrieve the current user's session from the incoming request. If it's not valid, you can throw an error which will terminate the upload flow. In the following example, we have a public file route that is protected by rate limiting, and a protected route that allows any authenticated user to upload files:

```ts
import { auth } from "auth";

import { createUploadthing, UploadThingError } from "uploadthing/server";

import { RateLimit } from "~/lib/ratelimit";

const ratelimiter = new RateLimit({
  /** rules */
});

export const uploadRouter = {
  publicRoute: f({ image: {} })
    .middleware(async ({ req }) => {
      const limit = await ratelimiter.verify(req);
      if (!limit.ok) {
        throw new UploadThingError("Rate limit exceeded");
      }

      return {};
    })
    .onUploadComplete(() => {
      /** ... */
    }),

  privateRoute: f({ image: {} })
    .middleware(async ({ req }) => {
      const session = await auth(req);
      if (!session) {
        throw new UploadThingError("You need to be logged in to upload files");
      }

      return { userId: session.user.id };
    })
    .onUploadComplete(() => {
      /** ... */
    }),
};
```

CopyCopied!

By throwing an `UploadThingError`, the error message is automatically sent down to the client. If throwing other errors, you need an [`errorFormatter`](https://docs.uploadthing.com/concepts/error-handling#error-formatting) to control what is sent down to the client.

UploadThing REST API Specification
You can use the UploadThing REST API to build SDKs for languages and frameworks we don't natively support. The API is designed to be simple and easy to use. The latest version of all endpoints are documented here.

Server
Server:https://api.uploadthing.com
Production


Authentication
ApiKeyAuth Required

ApiKeyAuth
Name
:
x-uploadthing-api-key
Value
:
QUxMIFlPVVIgQkFTRSBBUkUgQkVMT05HIFRPIFVT
Client Libraries

Curl
Curl Shell

default​#Copy link to "default"

GET
/v6/pollUpload/:fileKey
​#Copy link to "
/v6/pollUpload/:fileKey
"

Test Request
(get /v6/pollUpload/:fileKey)
Copy endpoint URL
Poll for upload complete.

Path Parameters
fileKey
string
required
Responses
200
object
Show Child Attributes
200
Copy content
{
  "status": "still working",
  "fileData": {
    "fileKey": "…",
    "fileName": "…",
    "fileSize": 1,
    "fileType": "…",
    "fileUrl": "…",
    "customId": "…",
    "callbackUrl": "…",
    "callbackSlug": "…"
  },
  "metadata": null,
  "callbackData": null
}
Poll for successful upload

GET
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/pollUpload/:fileKey \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'

GET
/v6/serverCallback
​#Copy link to "
/v6/serverCallback
"

Test Request
(get /v6/serverCallback)
Copy endpoint URL
Get server callback data. This is used to set the data returned from onUploadComplete callback.

Headers
authorization
string
required
The JWT token you got along with the presigned URLs from /prepareUpload

Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "status": "done"
}
Successfully retrieved callback data.

GET
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/serverCallback \
  --header 'Authorization: ' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'

POST
/v6/serverCallback
​#Copy link to "
/v6/serverCallback
"

Test Request
(post /v6/serverCallback)
Copy endpoint URL
Set server callback data. This is used to set the data returned from onUploadComplete callback.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
fileKey
string
max: 
300
required
callbackData
null |
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "status": "…"
}
Successfully set callback data.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/serverCallback \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "callbackData": null
}'

POST
/v6/prepareUpload
​#Copy link to "
/v6/prepareUpload
"

Test Request
(post /v6/prepareUpload)
Copy endpoint URL
Request presigned URLs for file uploads through based on your file router. NOTE: This spec complies with SDK versions ^6.4. Response may vary for older versions.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
callbackUrl
string
max: 
2048
uri
required
callbackSlug
string
max: 
128
required
files
array object[]
required
Show Child Attributes
routeConfig
anyOf
required
Show Child Attributes
Show Child Attributes
metadata
null |
Responses
200
array
Successfully retrieved presigned URLs.

Show Child Attributes
Show Child Attributes
Show Child Attributes
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
403
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
403
500
Copy content
[
  {
    "key": "…",
    "fileName": "…",
    "fileType": "…",
    "fileUrl": "…",
    "contentDisposition": "inline",
    "pollingJwt": "…",
    "pollingUrl": "…",
    "customId": "…",
    "url": "…",
    "fields": {
      "ANY_ADDITIONAL_PROPERTY": "…"
    }
  }
]
Successfully retrieved presigned URLs.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/prepareUpload \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "callbackUrl": "",
  "callbackSlug": "",
  "files": [
    {
      "name": "",
      "size": 1,
      "customId": null
    }
  ],
  "routeConfig": [
    "image"
  ],
  "metadata": null
}'

POST
/v6/uploadFiles
​#Copy link to "
/v6/uploadFiles
"

Test Request
(post /v6/uploadFiles)
Copy endpoint URL
Request presigned URLs for file uploads without file routes. NOTE: This spec complies with SDK versions ^6.4. Response may vary for older versions.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
files
array object[]
required
Show Child Attributes
acl
string
enum
public-read
private
metadata
null |
contentDisposition
string
enum
default: 
inline
inline
attachment
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "data": [
    {
      "key": "…",
      "fileName": "…",
      "fileType": "…",
      "fileUrl": "…",
      "contentDisposition": "inline",
      "pollingJwt": "…",
      "pollingUrl": "…",
      "customId": "…",
      "url": "…",
      "fields": {
        "ANY_ADDITIONAL_PROPERTY": "…"
      }
    }
  ]
}
Successfully retrieved presigned URLs.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/uploadFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "files": [
    {
      "name": "",
      "size": 1,
      "type": "",
      "customId": null
    }
  ],
  "acl": "public-read",
  "metadata": null,
  "contentDisposition": "inline"
}'

POST
/v6/completeMultipart
​#Copy link to "
/v6/completeMultipart
"

Test Request
(post /v6/completeMultipart)
Copy endpoint URL
Complete a multipart upload. This will finalize the upload and make the file available for download.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
fileKey
string
required
uploadId
string
required
etags
array object[]
required
Show Child Attributes
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "success": true
}
Successfully completed the multipart upload.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/completeMultipart \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "uploadId": "",
  "etags": [
    {
      "tag": "",
      "partNumber": 1
    }
  ]
}'

POST
/v6/listFiles
​#Copy link to "
/v6/listFiles
"

Test Request
(post /v6/listFiles)
Copy endpoint URL
List files for the current app. Response is paginated.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
limit
number
min: 
0
max: 
100000
default: 
500
The maximum number of files to retrieve.

offset
number
min: 
0
default: 
0
The number of files to skip.

Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "hasMore": true,
  "files": [
    {
      "id": "…",
      "customId": "my-custom-id",
      "key": "…",
      "name": "my-file.png",
      "status": "Uploaded",
      "size": 1024,
      "uploadedAt": 1717213483400
    }
  ]
}
Successfully retrieved files.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/listFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "limit": 500,
  "offset": 0
}'

POST
/v6/renameFiles
​#Copy link to "
/v6/renameFiles
"

Test Request
(post /v6/renameFiles)
Copy endpoint URL
Rename files.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
updates
array
required
Show Child Attributes
Show Child Attributes
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "success": true,
  "renamedCount": 1
}
Successfully renamed files.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/renameFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "updates": [
    {
      "newName": "",
      "fileKey": ""
    }
  ]
}'

POST
/v6/deleteFiles
​#Copy link to "
/v6/deleteFiles
"

Test Request
(post /v6/deleteFiles)
Copy endpoint URL
Mark files for deletion. The files will be deleted at the storage provider shortly after.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
files
deprecated
array string[]
A list of file ids

fileKeys
array string[]
A list of file keys

customIds
array string[]
A list of customIds

Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "success": true,
  "deletedCount": 1
}
Successfully marked file for deletion.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/deleteFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "files": [
    ""
  ],
  "fileKeys": [
    ""
  ],
  "customIds": [
    ""
  ]
}'

POST
/v7/getAppInfo
​#Copy link to "
/v7/getAppInfo
"

Test Request
(post /v7/getAppInfo)
Copy endpoint URL
Retrieve info for a given app

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "appId": "MY_APP_123",
  "defaultACL": "public-read",
  "allowACLOverride": false
}
Successfully retrieved app info.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v7/getAppInfo \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'

POST
/v6/getUsageInfo
​#Copy link to "
/v6/getUsageInfo
"

Test Request
(post /v6/getUsageInfo)
Copy endpoint URL
Retrieve usage info for the app associated with the provided API key.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "totalBytes": 26843545600,
  "appTotalBytes": 26843545600,
  "filesUploaded": 100000,
  "limitBytes": 107374182400
}
Successfully retrieved usage info.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/getUsageInfo \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'

POST
/v6/failureCallback
​#Copy link to "
/v6/failureCallback
"

Test Request
(post /v6/failureCallback)
Copy endpoint URL
Mark an upload as failed, or abort a multipart upload. This will free up resources and revert the storage quota.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
fileKey
string
max: 
300
required
The file key of the file that failed to upload.

uploadId
null | string
The uploadId, only applicable for multipart uploads.

Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "success": true
}
Successfully aborted or marked upload as failed.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/failureCallback \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "uploadId": null
}'

POST
/v6/requestFileAccess
​#Copy link to "
/v6/requestFileAccess
"

Test Request
(post /v6/requestFileAccess)
Copy endpoint URL
Request a presigned GET url for a private file.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
fileKey
string
max: 
300
The file key of the file to access.

customId
null | string
max: 
128
The custom id of the file to access.

expiresIn
number
min: 
1
max: 
604800
The number of seconds after which the URL expires. Defaults to what the app has set in the dashboard.

Example
3600
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
404
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
404
500
Copy content
{
  "ufsUrl": "https://APP_ID.ufs.sh/f/FILE_KEY",
  "url": "https://utfs.io/f/FILE_KEY"
}
Successfully retrieved a presigned GET URL.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/requestFileAccess \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "customId": null,
  "expiresIn": 3600
}'

POST
/v6/updateACL
​#Copy link to "
/v6/updateACL
"

Test Request
(post /v6/updateACL)
Copy endpoint URL
Update the ACL for a list of files.

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
updates
array
required
Show Child Attributes
Show Child Attributes
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "success": true,
  "updatedCount": 1
}
Successfully updated the ACL for files.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v6/updateACL \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "updates": [
    {
      "fileKey": "aaaa-bbbb-cccc-dddd",
      "acl": "public-read"
    }
  ]
}'

POST
/v7/prepareUpload
​#Copy link to "
/v7/prepareUpload
"

Test Request
(post /v7/prepareUpload)
Copy endpoint URL
Retrieve a presigned URL for a file upload. NOTE:: You can generate presigned URLs yourself directly on your server. Use this endpoint as a last resort if you're unable to generate valid signed URLs yourself. You can read more about generating your own presigned URLs here and how to upload files using the generated signed URL here: https://docs.uploadthing.com/uploading-files

Headers
x-uploadthing-api-key
string
required
The API key for the app

Example
sk_live_1234567890
x-uploadthing-version
string
A semver parseable version string of the SDK calling the API

Example
6.4.0
x-uploadthing-fe-package
string
Used for analytics, the package name of the frontend

Example
@uploadthing/react
x-uploadthing-be-adapter
string
Used for analytics, the name of the backend adapter

Example
express
Body
application/json
fileName
string
required
The name of the file to be uploaded

Example
image.png
fileSize
number
required
The size of the file to be uploaded, in bytes.

Example
1468006.4
slug
string
The slug of the file route used to upload this file. See https://docs.uploadthing.com/file-routes

Example
imageUploader
fileType
string
The type of the file to be uploaded.

Example
image/png
customId
string
A custom identifier for the file

Example
my-id-123
contentDisposition
string
enum
inline
attachment
acl
string
enum
public-read
private
expiresIn
number
default: 
3600
The number of seconds after which the file will be deleted from the bucket.

Example
3600
Responses
200
object
Show Child Attributes
400
object
Show Child Attributes
401
object
Show Child Attributes
500
object
Show Child Attributes
200
400
401
500
Copy content
{
  "key": "…",
  "url": "…"
}
Successfully retrieved app info.

POST
Selected HTTP client:Shell Curl

Curl
Copy content
curl https://api.uploadthing.com/v7/prepareUpload \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileName": "image.png",
  "fileSize": 1468006.4,
  "slug": "imageUploader",
  "fileType": "image/png",
  "customId": "my-id-123",
  "contentDisposition": "inline",
  "acl": "public-read",
  "expiresIn": 3600
}'

# UploadThing REST API Specification

You can use the UploadThing REST API to build SDKs for languages and frameworks we don't natively support. The API is designed to be simple and easy to use. The latest version of all endpoints are documented here.

Open Search(Keyboard Shortcut)⌃

v6.10.0

OAS 3.0.0

# UploadThing REST API

[Download OpenAPI Document](https://api.uploadthing.com/openapi-spec.json)

Server

Server: https://api.uploadthing.com

Production

AuthenticationApiKeyAuth Required

ApiKeyAuth

| Name : x-uploadthing-api-key |
| --- |
| Value : QUxMIFlPVVIgQkFTRSBBUkUgQkVMT05HIFRPIFVT |

Client Libraries

Shell

Ruby

Node.js

PHP

PythonSelect Client LibraryLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

More

Curl Shell

## default​

#Copy link to "default"

### 

GET

/v6/pollUpload/:fileKey

/v6/pollUpload/:fileKey

​

#Copy link to "

/v6/pollUpload/:fileKey

/v6/pollUpload/:fileKey

"

Test Request(get /v6/pollUpload/:fileKey)Copy endpoint URL

Poll for upload complete.

Path Parameters

-   fileKey
    
    string
    
    required
    

Responses

-   200
    
    object
    
    Show Child Attributes
    

200

Show Schema 

Copy content

```json
{
  "status": "still working",
  "fileData": {
    "fileKey": "…",
    "fileName": "…",
    "fileSize": 1,
    "fileType": "…",
    "fileUrl": "…",
    "customId": "…",
    "callbackUrl": "…",
    "callbackSlug": "…"
  },
  "metadata": null,
  "callbackData": null
}
```

Poll for successful upload

GET

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/pollUpload/:fileKey \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'
```

### 

GET

/v6/serverCallback

/v6/serverCallback

​

#Copy link to "

/v6/serverCallback

/v6/serverCallback

"

Test Request(get /v6/serverCallback)Copy endpoint URL

Get server callback data. This is used to set the data returned from `onUploadComplete` callback.

Headers

-   authorization
    
    string
    
    required
    
    The JWT token you got along with the presigned URLs from `/prepareUpload`
    

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "status": "done"
}
```

Successfully retrieved callback data.

GET

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/serverCallback \
  --header 'Authorization: ' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'
```

### 

POST

/v6/serverCallback

/v6/serverCallback

​

#Copy link to "

/v6/serverCallback

/v6/serverCallback

"

Test Request(post /v6/serverCallback)Copy endpoint URL

Set server callback data. This is used to set the data returned from `onUploadComplete` callback.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

fileKey

string

max: 

300

required

callbackData

null |

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "status": "…"
}
```

Successfully set callback data.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/serverCallback \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "callbackData": null
}'
```

### 

POST

/v6/prepareUpload

/v6/prepareUpload

​

#Copy link to "

/v6/prepareUpload

/v6/prepareUpload

"

Test Request(post /v6/prepareUpload)Copy endpoint URL

Request presigned URLs for file uploads through based on your file router. NOTE: This spec complies with SDK versions ^6.4. Response may vary for older versions.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

callbackUrl

string

max: 

2048uri

required

callbackSlug

string

max: 

128

required

files

array object\[\]

required

Show Child Attributes

routeConfig

anyOf

required

Show Child Attributes

Show Child Attributes

metadata

null |

Responses

-   200
    
    array
    
    Successfully retrieved presigned URLs.
    
    Show Child Attributes
    
    Show Child Attributes
    
    Show Child Attributes
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   403
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401403500

Show Schema 

Copy content

```json
[
  {
    "key": "…",
    "fileName": "…",
    "fileType": "…",
    "fileUrl": "…",
    "contentDisposition": "inline",
    "pollingJwt": "…",
    "pollingUrl": "…",
    "customId": "…",
    "url": "…",
    "fields": {
      "ANY_ADDITIONAL_PROPERTY": "…"
    }
  }
]
```

Successfully retrieved presigned URLs.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/prepareUpload \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "callbackUrl": "",
  "callbackSlug": "",
  "files": [
    {
      "name": "",
      "size": 1,
      "customId": null
    }
  ],
  "routeConfig": [
    "image"
  ],
  "metadata": null
}'
```

### 

POST

/v6/uploadFiles

/v6/uploadFiles

​

#Copy link to "

/v6/uploadFiles

/v6/uploadFiles

"

Test Request(post /v6/uploadFiles)Copy endpoint URL

Request presigned URLs for file uploads without file routes. NOTE: This spec complies with SDK versions ^6.4. Response may vary for older versions.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

files

array object\[\]

required

Show Child Attributes

acl

string enum

-   public-read
-   private

metadata

null |

contentDisposition

string enum

default: 

inline

-   inline
-   attachment

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "data": [
    {
      "key": "…",
      "fileName": "…",
      "fileType": "…",
      "fileUrl": "…",
      "contentDisposition": "inline",
      "pollingJwt": "…",
      "pollingUrl": "…",
      "customId": "…",
      "url": "…",
      "fields": {
        "ANY_ADDITIONAL_PROPERTY": "…"
      }
    }
  ]
}
```

Successfully retrieved presigned URLs.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/uploadFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "files": [
    {
      "name": "",
      "size": 1,
      "type": "",
      "customId": null
    }
  ],
  "acl": "public-read",
  "metadata": null,
  "contentDisposition": "inline"
}'
```

### 

POST

/v6/completeMultipart

/v6/completeMultipart

​

#Copy link to "

/v6/completeMultipart

/v6/completeMultipart

"

Test Request(post /v6/completeMultipart)Copy endpoint URL

Complete a multipart upload. This will finalize the upload and make the file available for download.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

fileKey

string

required

uploadId

string

required

etags

array object\[\]

required

Show Child Attributes

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "success": true
}
```

Successfully completed the multipart upload.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/completeMultipart \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "uploadId": "",
  "etags": [
    {
      "tag": "",
      "partNumber": 1
    }
  ]
}'
```

### 

POST

/v6/listFiles

/v6/listFiles

​

#Copy link to "

/v6/listFiles

/v6/listFiles

"

Test Request(post /v6/listFiles)Copy endpoint URL

List files for the current app. Response is paginated.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

limit

number

min: 

0

max: 

100000

default: 

500

The maximum number of files to retrieve.

offset

number

min: 

0

default: 

0

The number of files to skip.

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "hasMore": true,
  "files": [
    {
      "id": "…",
      "customId": "my-custom-id",
      "key": "…",
      "name": "my-file.png",
      "status": "Uploaded",
      "size": 1024,
      "uploadedAt": 1717213483400
    }
  ]
}
```

Successfully retrieved files.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/listFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "limit": 500,
  "offset": 0
}'
```

### 

POST

/v6/renameFiles

/v6/renameFiles

​

#Copy link to "

/v6/renameFiles

/v6/renameFiles

"

Test Request(post /v6/renameFiles)Copy endpoint URL

Rename files.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

updates

array

required

Show Child Attributes

Show Child Attributes

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "success": true,
  "renamedCount": 1
}
```

Successfully renamed files.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/renameFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "updates": [
    {
      "newName": "",
      "fileKey": ""
    }
  ]
}'
```

### 

POST

/v6/deleteFiles

/v6/deleteFiles

​

#Copy link to "

/v6/deleteFiles

/v6/deleteFiles

"

Test Request(post /v6/deleteFiles)Copy endpoint URL

Mark files for deletion. The files will be deleted at the storage provider shortly after.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

files

deprecated

array string\[\]

A list of file ids

fileKeys

array string\[\]

A list of file keys

customIds

array string\[\]

A list of customIds

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "success": true,
  "deletedCount": 1
}
```

Successfully marked file for deletion.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/deleteFiles \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "files": [
    ""
  ],
  "fileKeys": [
    ""
  ],
  "customIds": [
    ""
  ]
}'
```

### 

POST

/v7/getAppInfo

/v7/getAppInfo

​

#Copy link to "

/v7/getAppInfo

/v7/getAppInfo

"

Test Request(post /v7/getAppInfo)Copy endpoint URL

Retrieve info for a given app

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "appId": "MY_APP_123",
  "defaultACL": "public-read",
  "allowACLOverride": false
}
```

Successfully retrieved app info.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v7/getAppInfo \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'
```

### 

POST

/v6/getUsageInfo

/v6/getUsageInfo

​

#Copy link to "

/v6/getUsageInfo

/v6/getUsageInfo

"

Test Request(post /v6/getUsageInfo)Copy endpoint URL

Retrieve usage info for the app associated with the provided API key.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "totalBytes": 26843545600,
  "appTotalBytes": 26843545600,
  "filesUploaded": 100000,
  "limitBytes": 107374182400
}
```

Successfully retrieved usage info.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/getUsageInfo \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN'
```

### 

POST

/v6/failureCallback

/v6/failureCallback

​

#Copy link to "

/v6/failureCallback

/v6/failureCallback

"

Test Request(post /v6/failureCallback)Copy endpoint URL

Mark an upload as failed, or abort a multipart upload. This will free up resources and revert the storage quota.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

fileKey

string

max: 

300

required

The file key of the file that failed to upload.

uploadId

null | string

The uploadId, only applicable for multipart uploads.

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "success": true
}
```

Successfully aborted or marked upload as failed.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/failureCallback \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "uploadId": null
}'
```

### 

POST

/v6/requestFileAccess

/v6/requestFileAccess

​

#Copy link to "

/v6/requestFileAccess

/v6/requestFileAccess

"

Test Request(post /v6/requestFileAccess)Copy endpoint URL

Request a presigned GET url for a private file.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

fileKey

string

max: 

300

The file key of the file to access.

customId

null | string

max: 

128

The custom id of the file to access.

expiresIn

number

min: 

1

max: 

604800

The number of seconds after which the URL expires. Defaults to what the app has set in the dashboard.

Example`3600`

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   404
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401404500

Show Schema 

Copy content

```json
{
  "ufsUrl": "https://APP_ID.ufs.sh/f/FILE_KEY",
  "url": "https://utfs.io/f/FILE_KEY"
}
```

Successfully retrieved a presigned GET URL.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/requestFileAccess \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "fileKey": "",
  "customId": null,
  "expiresIn": 3600
}'
```

### 

POST

/v6/updateACL

/v6/updateACL

​

#Copy link to "

/v6/updateACL

/v6/updateACL

"

Test Request(post /v6/updateACL)Copy endpoint URL

Update the ACL for a list of files.

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

updates

array

required

Show Child Attributes

Show Child Attributes

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "success": true,
  "updatedCount": 1
}
```

Successfully updated the ACL for files.

POST

Selected HTTP client: Shell CurlLibcurlHttpClientRestSharpclj-httpHttpNewRequestHTTP/1.1AsyncHttpjava.net.httpOkHttpUnirestFetchAxiosofetchjQueryXHROkHttpFetchAxiosofetchundiciNSURLSessionCohttpcURLGuzzleInvoke-WebRequestInvoke-RestMethodhttp.clientRequestshttrnet::httpCurlWgetHTTPieNSURLSession

Copy content

```curl
curl https://api.uploadthing.com/v6/updateACL \
  --request POST \
  --header 'X-Uploadthing-Api-Key: sk_live_1234567890' \
  --header 'X-Uploadthing-Api-Key: YOUR_SECRET_TOKEN' \
  --data '{
  "updates": [
    {
      "fileKey": "aaaa-bbbb-cccc-dddd",
      "acl": "public-read"
    }
  ]
}'
```

### 

POST

/v7/prepareUpload

/v7/prepareUpload

​

#Copy link to "

/v7/prepareUpload

/v7/prepareUpload

"

Test Request(post /v7/prepareUpload)Copy endpoint URL

Retrieve a presigned URL for a file upload. NOTE:: You can generate presigned URLs yourself directly on your server. Use this endpoint as a last resort if you're unable to generate valid signed URLs yourself. You can read more about generating your own presigned URLs here and how to upload files using the generated signed URL here: [https://docs.uploadthing.com/uploading-files](https://docs.uploadthing.com/uploading-files)

Headers

-   x-uploadthing-api-key
    
    string
    
    required
    
    The API key for the app
    
    Example`sk_live_1234567890`
    
-   x-uploadthing-version
    
    string
    
    A semver parseable version string of the SDK calling the API
    
    Example`6.4.0`
    
-   x-uploadthing-fe-package
    
    string
    
    Used for analytics, the package name of the frontend
    
    Example`@uploadthing/react`
    
-   x-uploadthing-be-adapter
    
    string
    
    Used for analytics, the name of the backend adapter
    
    Example`express`
    

Body

application/json

Hide Child Attributes

fileName

string

required

The name of the file to be uploaded

Example`image.png`

fileSize

number

required

The size of the file to be uploaded, in bytes.

Example`1468006.4`

slug

string

The slug of the file route used to upload this file. See [https://docs.uploadthing.com/file-routes](https://docs.uploadthing.com/file-routes)

Example`imageUploader`

fileType

string

The type of the file to be uploaded.

Example`image/png`

customId

string

A custom identifier for the file

Example`my-id-123`

contentDisposition

string enum

-   inline
-   attachment

acl

string enum

-   public-read
-   private

expiresIn

number

default: 

3600

The number of seconds after which the file will be deleted from the bucket.

Example`3600`

Responses

-   200
    
    object
    
    Show Child Attributes
    
-   400
    
    object
    
    Show Child Attributes
    
-   401
    
    object
    
    Show Child Attributes
    
-   500
    
    object
    
    Show Child Attributes
    

200400401500

Show Schema 

Copy content

```json
{
  "key": "…",
  "url": "…"
}
```

Success