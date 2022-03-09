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
        self.aggrFleetData = {}
        self.records = []

        self.init()

    def init(self):
        logger.debug("in FleetStatsAggregator init")

        self.aggrFleetData = {}

        # Read csv from S3
        s3_data = appCommon.s3.get_object(Bucket=self.s3Bucket, Key=self.s3Key)

        self.records = []

        for record in csv.DictReader(codecs.getreader("utf-8")(s3_data["Body"])):
            self.records.append(record)
            overProvInstance = appCommon.OverProvInstance(
                record, self.metricType)

            # if overProvInstance.finding == "OVER_PROVISIONED":
            FleetStatsAggregator.aggregateFleetStatsForInstance(
                overProvInstance,
                self.aggrFleetData
            )

        # for each fleet+instanceType entry in aggregate data, append additional fleet level info

        for tag in self.aggrFleetData:
            utilByInstType = self.aggrFleetData[tag]

            for instanceType in utilByInstType:
                utilData = utilByInstType.get(instanceType)

                totalInstCntForInstType = utilData.get(appCommon.totalInstCnt_FN)

                utilData[appCommon.totalFleetInstCnt_FN] = totalInstCntForInstType

                avgVCpuUtil = utilData.get(appCommon.totalVCpuUtil_FN) / totalInstCntForInstType

                utilData[appCommon.avgFleetVCpuUtil_FN] = avgVCpuUtil

                memUtilReportingInstCnt = utilData.get(appCommon.memUtilReportingInstCnt_FN)

                if (memUtilReportingInstCnt == None or memUtilReportingInstCnt != totalInstCntForInstType):
                    utilData[appCommon.hasAvgFleetMemUtil_FN] = False
                    utilData[appCommon.avgFleetMemUtil_FN] = 'not available'
                else:
                    utilData[appCommon.hasAvgFleetMemUtil_FN] = True

                    avgMemUtil = utilData.get(appCommon.totalMemUtil_FN) / totalInstCntForInstType

                    utilData[appCommon.avgFleetMemUtil_FN] = avgMemUtil

    def getAggregatedFleetData(self):
        logger.debug("in getAggregatedFleetData")

        return self.aggrFleetData

    def getCsvRecords(self):
        logger.debug("in getCSVRecords")
        return self.records

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

            if (overProvInstance.memUtil != None and overProvInstance.memUtil != ""):
                totalFleetMemUtil = dataByInstanceType.get(
                    appCommon.totalMemUtil_FN)

                dataByInstanceType[appCommon.totalMemUtil_FN] = float(
                    overProvInstance.memUtil) if totalFleetMemUtil == None else totalFleetMemUtil + float(
                    overProvInstance.memUtil)

                memUtilReportingInstCnt = dataByInstanceType.get(
                    appCommon.memUtilReportingInstCnt_FN)

                dataByInstanceType[appCommon.memUtilReportingInstCnt_FN] = 1 \
                    if memUtilReportingInstCnt == None else memUtilReportingInstCnt + 1

        return data
