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

import csv
import codecs
import appCommon as appCommon
import logging

logger = logging.getLogger()


class FleetStatsAggregator():

    def __init__(self, s3Bucket, s3Key, metricType):
        self.s3Bucket = s3Bucket
        self.s3Key = s3Key
        self.metricType = metricType

    @staticmethod
    def aggregateFleetStatsForInstance(
        overProvInstance,
        aggrFleetData
    ):

        data = {}

        data[appCommon.overProvInstanceArn_FN] = overProvInstance.instanceArn
        data[appCommon.overProvInstanceName_FN] = overProvInstance.instanceName
        data[appCommon.overProvInstanceType_FN] = overProvInstance.instanceType
        data[appCommon.tag_FN] = overProvInstance.tag

        data[appCommon.cpuUtilizationNumeric_FN] = float(
            overProvInstance.cpuUtil)
        data[appCommon.cpuUtilization_FN] = "{:.2f}".format(
            float(overProvInstance.cpuUtil)) + " %"

        data[appCommon.memUtilization_FN] = "{:.2f}".format(float(
            overProvInstance.memUtil)) + " %" if overProvInstance.memUtil != None and overProvInstance.memUtil != "" else appCommon.notAvailTxt

        if overProvInstance.tag != None and overProvInstance.tag != "":
            # track vcpu util across fleet by instance type
            fleetData = aggrFleetData.get(overProvInstance.tag)
            if fleetData == None:
                fleetData = {}
                aggrFleetData[overProvInstance.tag] = fleetData

            dataByInstanceType = fleetData.get(overProvInstance.instanceType)
            if dataByInstanceType == None:
                dataByInstanceType = {}
                fleetData[overProvInstance.instanceType] = dataByInstanceType

            totalFleetInstCnt = dataByInstanceType.get(
                appCommon.totalInstCnt_FN)

            dataByInstanceType[appCommon.totalInstCnt_FN] = 1 if totalFleetInstCnt == None else totalFleetInstCnt + 1

            totalFleetVCpuUtil = dataByInstanceType.get(
                appCommon.totalVCpuUtil_FN)

            dataByInstanceType[appCommon.totalVCpuUtil_FN] = float(
                overProvInstance.cpuUtil) if totalFleetVCpuUtil == None else totalFleetVCpuUtil + float(
                overProvInstance.cpuUtil)

        return data

    def augmentFleetAggrStatsToCOReport(self):
        aggrFleetData = {}

        # Read csv from S3
        s3_data = appCommon.s3.get_object(Bucket=self.s3Bucket, Key=self.s3Key)

        overProvInstancesWithAggrData = []

        for record in csv.DictReader(codecs.getreader("utf-8")(s3_data["Body"])):

            overProvInstance = appCommon.OverProvInstance(
                record, self.metricType)

            if overProvInstance.finding == "OVER_PROVISIONED":
                overProvInstancesWithAggrData.append(
                    FleetStatsAggregator.aggregateFleetStatsForInstance(
                        overProvInstance,
                        aggrFleetData
                    )
                )

        # for each row in overProvInstLst, append the total fleet size corresponding to that instance's fleet membership
        # by matching instance name and also append the average cpu util for that fleet
        for overProvInstanceWithAggr in overProvInstancesWithAggrData:
            overProvInstType = overProvInstanceWithAggr[appCommon.overProvInstanceType_FN]
            tag = overProvInstanceWithAggr.get(appCommon.tag_FN)
            if tag == None or tag == "":
                logger.debug("skipping record for instance %s, since its tag is not set",
                             overProvInstanceWithAggr[appCommon.overProvInstanceArn_FN])
                overProvInstanceWithAggr[appCommon.tag_FN] = ""
                overProvInstanceWithAggr[appCommon.avgFleetVCpuUtil_FN] = appCommon.notAvailTxt
                overProvInstanceWithAggr[appCommon.totalFleetInstCnt_FN] = appCommon.notAvailTxt
            else:
                utilByInstType = aggrFleetData.get(tag)
                utilData = utilByInstType.get(overProvInstType)
                avgVCpuUtil = utilData.get(
                    appCommon.totalVCpuUtil_FN) / utilData.get(appCommon.totalInstCnt_FN)

                overProvInstanceWithAggr[appCommon.avgFleetVCpuUtil_FN] = "{:.2f}".format(
                    avgVCpuUtil) + " %"
                overProvInstanceWithAggr[appCommon.totalFleetInstCnt_FN] = utilData.get(
                    appCommon.totalInstCnt_FN)

                # check if the avg is within + or - 5% when compared to this particular instances
                overProvInstanceWithAggr[appCommon.isCpuUtilWithin5Percent_FN] = True \
                    if abs(overProvInstanceWithAggr[appCommon.cpuUtilizationNumeric_FN] - avgVCpuUtil) \
                    <= appCommon.cpu_util_delta_with_fleet_avg else False

        return overProvInstancesWithAggrData
