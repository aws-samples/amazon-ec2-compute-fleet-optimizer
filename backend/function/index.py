####################################################################################
# Copyright Amazon.com Inc. or its affiliates.
#
# SPDX-License-Identifier: MIT No Attribution(MIT-0)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
####################################################################################

import json
import os
import appCommon as appCommon
import logging
from fleetStatsAggregator import FleetStatsAggregator
from overProvInstanceOptimizer import OverProvInstanceOptimizer

logger = logging.getLogger()
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARN').upper()
logger.setLevel(LOGLEVEL)

s3BucketEnvVarName = os.environ['S3_BUCKET_ENV_VAR_NAME']
s3Bucket = os.environ[s3BucketEnvVarName]

class ComputeFleetOptimizerHdlr():

    def __init__(self):
        pass

    def __call__(self, event, context):

        try:

            response = {}

            evtBody = json.loads(event["body"])
            s3Key = evtBody["s3KeyName"]

            logger.info("s3 bucket from env var: %s, eventBody: %s",
                        s3Bucket, evtBody)

            # indicates which utilization metric to utilize for recommendation
            # hardcode this parameter since AWS Compute Optimizer only exports the Max utilization metrics at the current time
            metricType = appCommon.max_metric

            requestType = evtBody["requestType"]

            if requestType == "aggregateFleetLevelStats":
                aggregator = FleetStatsAggregator(s3Bucket, s3Key, metricType)
                response = aggregator.augmentFleetAggrStatsToCOReport()
            elif requestType == "optimizeComputeFleet":
                optimizer = OverProvInstanceOptimizer(s3Bucket, s3Key, metricType,
                                                      evtBody[appCommon.overProvInstanceArn_FN],
                                                      int(evtBody[appCommon.overProvInstanceCount_FN]),
                                                      float(evtBody[appCommon.maxCpuUtilCriteria_FN]),
                                                      float(evtBody[appCommon.maxMemUtilCriteria_FN]),
                                                      float(evtBody[appCommon.perfGainedGrav2Criteria_FN]),
                                                      evtBody[appCommon.isMaximizeCpuUtilCrit_FN],
                                                      evtBody[appCommon.isMaximizeMemUtilCrit_FN])
                response = optimizer.optimizeComputeForSavings()
            else:
                raise Exception("Invalid requestType parameter provided!")

            respBody = json.dumps(response)
            logger.info(respBody)

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "text/json",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": respBody
            }
        except Exception as e:
            logger.error(e)
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "text/json",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps({"error": repr(e)})
            }

handler = ComputeFleetOptimizerHdlr()
