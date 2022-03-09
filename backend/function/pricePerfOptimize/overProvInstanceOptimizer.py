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

import re
import math
import appCommon as appCommon
import logging
from fleetStatsAggregator import FleetStatsAggregator

logger = logging.getLogger()


class OverProvInstanceOptimizer():

    def __init__(self, s3Bucket, s3Key, metricType, fleetId, fleetInstanceType, hasGravitonPerfGainCriteria,
                 perfGainGrav2Crit, isMaximizeCpuUtil, maxCpuUtilCrit,
                 isMaximizeMemUtil, maxMemUtilCrit):
        logger.debug("in cotr of OverProvInstanceOptimizer")

        self.s3Bucket = s3Bucket
        self.s3Key = s3Key
        self.metricType = metricType
        self.fleetTag = fleetId
        self.fleetInstanceType = fleetInstanceType
        self.maxCpuUtilCrit = maxCpuUtilCrit
        self.maxMemUtilCrit = maxMemUtilCrit
        self.perfGainGrav2Crit = perfGainGrav2Crit
        self.hasGravitonPerfGainCriteria = hasGravitonPerfGainCriteria
        self.isMaximizeCpuUtil = isMaximizeCpuUtil
        self.isMaximizeMemUtil = isMaximizeMemUtil

        self.fleetInstanceCnt = 0
        self.fleetAvgCpuUtil = 0
        self.fleetMemReportingInstanceCnt = 0
        self.fleetAvgMemUtil = 0

        self.aggrFleetData = {}

        # ec2 instance in fleet with cpu util closest to the average cpu util of fleet
        self.representativeEc2Instance = None
        self.recoList = []

        self.init()

    def init(self):
        logger.debug("in overProvInstanceOptimizer init")

        aggregator = FleetStatsAggregator(self.s3Bucket, self.s3Key, self.metricType)

        self.aggrFleetData = aggregator.getAggregatedFleetData()

        lowestCpuUtilDeviationRecord = None
        lowestCpuUtilDeviation = None

        fleetCpuUtilByInstType = self.aggrFleetData.get(self.fleetTag)
        fleetUtilData = fleetCpuUtilByInstType.get(self.fleetInstanceType)

        self.fleetAvgCpuUtil = fleetUtilData.get(appCommon.avgFleetVCpuUtil_FN)
        self.fleetInstanceCnt = fleetUtilData.get(appCommon.totalInstCnt_FN)

        self.fleetHasAvgFleetMemUtil = fleetUtilData.get(appCommon.hasAvgFleetMemUtil_FN)
        self.fleetAvgMemUtil = fleetUtilData.get(appCommon.avgFleetMemUtil_FN)
        self.fleetMemReportingInstanceCnt = fleetUtilData.get(appCommon.memUtilReportingInstCnt_FN)

        for record in aggregator.getCsvRecords():

            overProvInstance = appCommon.OverProvInstance(
                record, self.metricType)

            # if overProvInstance.finding != "OVER_PROVISIONED" or \
            if overProvInstance.tag != self.fleetTag or \
                    overProvInstance.instanceType != self.fleetInstanceType:

                continue

            cpuUtilDeviation = abs(float(overProvInstance.cpuUtil) - self.fleetAvgCpuUtil)

            if lowestCpuUtilDeviation == None or cpuUtilDeviation < lowestCpuUtilDeviation:

                lowestCpuUtilDeviation = cpuUtilDeviation
                lowestCpuUtilDeviationRecord = record

        self.representativeEc2Instance = appCommon.OverProvInstance(
            lowestCpuUtilDeviationRecord, self.metricType)

        self.recoList = []
        recoCnt = int(self.representativeEc2Instance.recommendationCnt)
        i = 1
        while i <= recoCnt:
            instanceType = lowestCpuUtilDeviationRecord[appCommon.getRecoInstanceTypeFN(str(i))]
            if not instanceType.startswith('t4'):
                self.recoList.append(appCommon.RecommendedInstance(
                    lowestCpuUtilDeviationRecord, str(i), self.metricType))
            i += 1

    # get optimized vCPU count
    @staticmethod
    def getVcpuOptimization(
        currVcpuCnt,
        fleetInstanceCnt,
        fleetAvgCpuUtil,
        hasGravitonPerfGainCriteria,
        perfGainGrav2Crit,
        isMaximizeCpuUtil,
        maxCpuUtilCrit
    ):
        logger.debug("in getVcpuOptimization")

        hasCpuUtilMaxReducedCpuCnt = False

        # let's use the currently deployed total cpu count of the fleet as the starting value
        # for the optimized total cpu count, as we'll optimize this iteratively in below steps
        optimizedTotalCpuCnt = currVcpuCnt * fleetInstanceCnt
        optimizedCpuUtil = fleetAvgCpuUtil

        if hasGravitonPerfGainCriteria:
            # apply the Grav2 perf improvements from input criteria to the vcpu count
            # scaledTotalCpuCnt = scaledTotalCpuCnt * (100 / (100 + perfGainGrav2Crit))
            optimizedTotalCpuCnt = optimizedTotalCpuCnt / (1 + (perfGainGrav2Crit/100))

            logger.debug("optimizedTotalCpuCnt with just Graviton perf benefit = %f", optimizedTotalCpuCnt)

        # if input criteria was to maximize cpu utilization, only then scale/adjust the util further and derive corresponding cpu count
        if isMaximizeCpuUtil:
            # compare scaledCpuUtil against maxCpuUtilCrit in order to adjust the recoVcpuCnt
            # such that new Vcpu count corresponds with the diff in utilization

            # calculate cpu needed for maxCpuUtilCrit
            cpuUtilMaximizedTotalCpuCnt = fleetAvgCpuUtil * optimizedTotalCpuCnt / maxCpuUtilCrit
            if cpuUtilMaximizedTotalCpuCnt < optimizedTotalCpuCnt:
                hasCpuUtilMaxReducedCpuCnt = True

            optimizedTotalCpuCnt = cpuUtilMaximizedTotalCpuCnt

            logger.debug("optimizedTotalCpuCnt = %f",
                         optimizedTotalCpuCnt)

            optimizedCpuUtil = maxCpuUtilCrit

        data = {}
        data[appCommon.hasCpuUtilMaximizeReducedCpu_FN] = hasCpuUtilMaxReducedCpuCnt
        data[appCommon.totalVcpus_FN] = optimizedTotalCpuCnt
        data[appCommon.vcpuUtil_FN] = optimizedCpuUtil

        return data

    # get optimized memory
    @staticmethod
    def getMemOptimization(
        currMem,
        fleetInstanceCnt,
        fleetAvgMemUtil,
        maxMemUtilCrit
    ):
        logger.debug("in getMemOptimization")

        # let's use the currently deployed total memory  of the fleet as the starting value
        # for the optimized total memory, as we'll optimize this in below step
        optimizedTotalMem = currMem * fleetInstanceCnt

        # compare scaledCpuUtil against maxCpuUtilCrit in order to adjust the recoVcpuCnt
        # such that new Vcpu count corresponds with the diff in utilization

        # calculate cpu needed for maxCpuUtilCrit
        optimizedTotalMem = fleetAvgMemUtil * optimizedTotalMem / maxMemUtilCrit

        optimizedMemUtil = maxMemUtilCrit

        logger.debug("optimizedTotalMem = %f", optimizedTotalMem)

        data = {}
        data[appCommon.totalMem_FN] = optimizedTotalMem
        data[appCommon.memUtilization_FN] = optimizedMemUtil

        return data

    @staticmethod
    def getPerfRiskLevel(recoPerfRisk):
        if recoPerfRisk == "0":
            recoPerfRiskLevel = "Very Low"
        elif recoPerfRisk == "1":
            recoPerfRiskLevel = "Low"
        elif recoPerfRisk == "2":
            recoPerfRiskLevel = "Medium"
        elif recoPerfRisk == "3":
            recoPerfRiskLevel = "High"
        elif recoPerfRisk == "4":
            recoPerfRiskLevel = "Very High"
        else:
            recoPerfRiskLevel = appCommon.notAvailTxt
        return recoPerfRiskLevel

    def optimizeWithRecommendedInstance(self,
                                        recoInstance
                                        ):
        logger.debug("in optimizeWithRecommendedInstance")

        data = {}
        computedRisk = None

        recoVcpuCntPerInstance = int(recoInstance.vcpuCntPerInstance)

        recoMem, recoMemUnit = re.search(
            "(.*)\s+(.*)", recoInstance.memPerInstance).group(1, 2)
        recoMemPerInstance = float(recoMem)

        # optimize for vCPU
        vcpuOptResult = OverProvInstanceOptimizer.getVcpuOptimization(
            int(self.representativeEc2Instance.vcpus),
            self.fleetInstanceCnt,
            self.fleetAvgCpuUtil,
            self.hasGravitonPerfGainCriteria,
            self.perfGainGrav2Crit,
            self.isMaximizeCpuUtil,
            self.maxCpuUtilCrit
        )

        data[appCommon.recoProjectedMaxVcpuUtil_FN] = "{:.2f}".format(
            vcpuOptResult[appCommon.vcpuUtil_FN]) + " %"

        data[appCommon.recoProjectedMaxMemUtilTxt] = appCommon.notAvailTxt
        requiredTotalVcpuCnt = vcpuOptResult[appCommon.totalVcpus_FN]

        # optimize for memory ONLY if the current memory utilization metric value is available
        if self.isMaximizeMemUtil and self.fleetHasAvgFleetMemUtil:
            memOptResult = OverProvInstanceOptimizer.getMemOptimization(
                int(self.representativeEc2Instance.mem),
                self.fleetInstanceCnt,
                self.fleetAvgMemUtil,
                self.maxMemUtilCrit)

            memUtilFromMemOpt = memOptResult[appCommon.memUtilization_FN]

            vcpuCntFromMemOpt = memOptResult[appCommon.totalMem_FN] * (
                recoVcpuCntPerInstance / recoMemPerInstance
            )

            if memUtilFromMemOpt != None and memUtilFromMemOpt > 0:
                data[appCommon.recoProjectedMaxMemUtilTxt] = "{:.2f}".format(
                    memUtilFromMemOpt) + " %"

            # adjust the vpcuCnt required for the reco instance,
            # after taking both vcpu and mem optimizations
            requiredTotalVcpuCnt = max(requiredTotalVcpuCnt, vcpuCntFromMemOpt)

        else:
            # if memory usage wasn't taken into optimizing, then the risk of the recommendation
            # is high

            if (vcpuOptResult[appCommon.hasCpuUtilMaximizeReducedCpu_FN]):
                computedRisk = 3  # 3 is 'high risk'

        # compute required total instances for this reco
        totalInstance = int(requiredTotalVcpuCnt / recoVcpuCntPerInstance) + \
            1 if requiredTotalVcpuCnt % recoVcpuCntPerInstance > 0 else requiredTotalVcpuCnt / \
            recoVcpuCntPerInstance
        data[appCommon.recoTotalVcpus_FN] = totalInstance * \
            recoVcpuCntPerInstance
        data[appCommon.recoTotalMem_FN] = (
            "{:0.0f}".format(totalInstance * recoMemPerInstance) +
            " " + recoMemUnit
        )
        data[appCommon.recoTotalInstances_FN] = totalInstance

        recoCostTotalMonth = totalInstance * \
            float(recoInstance.hourlyOnDemandPrice) * 730
        data[appCommon.recoTotalMonthlyCost_FN] = int(
            math.ceil(recoCostTotalMonth))

        perfRisk = computedRisk if computedRisk != None else recoInstance.perfRisk
        recoPerfRisk = str(
            perfRisk) if perfRisk != None else appCommon.notApplicableTxt
        data[appCommon.recoPerfRisk_FN] = OverProvInstanceOptimizer.getPerfRiskLevel(
            recoPerfRisk)

        return data

    def optimizeComputeForSavings(self):
        logger.debug("in optimizeComputeForSavings")

        data = {}

        currMem, memUnit = re.search(
            "(.*)\s+(.*)", self.representativeEc2Instance.mem).group(1, 2)

        data[appCommon.overProvInstanceArn_FN] = self.representativeEc2Instance.instanceArn
        data[appCommon.overProvInstanceName_FN] = self.representativeEc2Instance.instanceName
        data[appCommon.overProvInstanceType_FN] = self.representativeEc2Instance.instanceType
        data[appCommon.tag_FN] = self.representativeEc2Instance.tag

        data[appCommon.cpuUtilizationNumeric_FN] = float(
            self.representativeEc2Instance.cpuUtil)
        data[appCommon.cpuUtilization_FN] = "{:.2f}".format(
            float(self.representativeEc2Instance.cpuUtil)) + " %"

        data[appCommon.memUtilization_FN] = "{:.2f}".format(
            float(self.representativeEc2Instance.memUtil)) + " %" \
            if (self.representativeEc2Instance.memUtil != None and self.representativeEc2Instance.memUtil != "") \
            else appCommon.notAvailTxt

        # for full detail report, add each reco for the overprovisioned instance

        data[appCommon.currentTotalVcpus_FN] = int(
            self.representativeEc2Instance.vcpus) * self.fleetInstanceCnt
        data[appCommon.currentTotalMem_FN] = str(
            float(currMem) * self.fleetInstanceCnt) + " " + memUnit
        data[appCommon.currentTotalInstances_FN] = self.fleetInstanceCnt
        currentTotalMonthlyCost = self.fleetInstanceCnt * \
            float(self.representativeEc2Instance.hourlyOnDemandPrice) * 730
        data[appCommon.currentTotalMonthlyCost_FN] = "${:0,.0f}".format(
            math.ceil(currentTotalMonthlyCost)
        )

        optimizedFleetRecoList = []

        # process each instance recommended by Compute Optimizer
        for recoInstance in self.recoList:

            optimizedFleetReco = self.optimizeWithRecommendedInstance(
                recoInstance
            )

            optimizedFleetReco[appCommon.recoInstanceType_FN] = recoInstance.instanceType

            recoTotalMonthlyCost = optimizedFleetReco[appCommon.recoTotalMonthlyCost_FN]

            priceDiff = math.ceil(recoTotalMonthlyCost -
                                  currentTotalMonthlyCost)

            priceDiffPercent = (priceDiff / currentTotalMonthlyCost) * 100

            priceDiff = "${:0,.0f}".format(priceDiff).replace("$-", "-$")
            priceDiffPercent = (
                "{:.2f}".format(priceDiffPercent).replace("$-", "-$") + " %"
            )

            optimizedFleetReco[appCommon.recoPriceDiff_FN] = priceDiff
            optimizedFleetReco[appCommon.recoPriceDiffPercent_FN] = priceDiffPercent
            optimizedFleetReco[appCommon.recoTotalMonthlyCost_FN] = "${:0,.0f}".format(
                math.ceil(recoTotalMonthlyCost)
            )

            optimizedFleetRecoList.append(optimizedFleetReco)

        data[appCommon.recommendations_FN] = optimizedFleetRecoList

        return data
