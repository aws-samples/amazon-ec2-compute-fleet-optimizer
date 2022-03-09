/* Amplify Params - DO NOT EDIT
	ENV
	REGION
	STORAGE_COMPUTEFLEETOPTE_BUCKETNAME
	S3_BUCKET_ENV_VAR_NAME
Amplify Params - DO NOT EDIT */

/**
 * @type {import('@types/aws-lambda').APIGatewayProxyHandler}
 */

'use strict'

const { v4: uuidv4 } = require('uuid')
const AWS = require('aws-sdk')
AWS.config.update({ region: process.env.AWS_REGION })
const s3 = new AWS.S3({
  region: process.env.REGION,
})
// Main Lambda entry point
exports.handler = async (event) => {
  console.log(`EVENT: ${JSON.stringify(event)}`);
  const result = await getUploadURL()
  console.log('Result: ', result)
  return result
}

const getUploadURL = async function() {
  const actionId = uuidv4()
  var keys = process.env  
  let bucketVarName =  process.env.S3_BUCKET_ENV_VAR_NAME
  console.log('bucketVarName: ', bucketVarName)
  const bucket = keys[bucketVarName]
  console.log('bucket: ', bucket)
  const s3Params = {
    Bucket: bucket,
    Key:  `${actionId}.csv`,
    ContentType: 'text/csv' // Update to match whichever content type you need to upload
    //ACL: 'public-read'      // Enable this setting to make the object publicly readable - only works if the bucket can support public objects
  }

  console.log('getUploadURL: ', s3Params)
  return new Promise((resolve, reject) => {
    // Get signed URL
    resolve({
      "statusCode": 200,
      "isBase64Encoded": false,
      "headers": {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*"
      },
      "body": JSON.stringify({
          "uploadURL": s3.getSignedUrl('putObject', s3Params),
          "objectKey": `${actionId}.csv`
      })
    })
  })
}
