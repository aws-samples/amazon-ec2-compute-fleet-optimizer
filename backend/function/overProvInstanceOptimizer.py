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
import csv
import codecs
import math
import appCommon as appCommon
import logging

logger = logging.getLogger()


class OverProvInstanceOptimizer():

    def __init__(self, s3Bucket, s3Key, metricType, overProvInstArn, overProvInstCnt,
                 maxCpuUtilCrit, maxMemUtilCrit, perfGainGrav2Crit,
                 isMaximizeCpuUtil, isMaximizeMemUtil):
        logger.debug("in cotr of OverProvInstanceOptimizer")

        self.s3Bucket = s3Bucket
        self.s3Key = s3Key
        self.metricType = metricType
        self.overProvInstArn = overProvInstArn
        self.overProvInstCnt = overProvInstCnt
        self.maxCpuUtilCrit = maxCpuUtilCrit
        self.maxMemUtilCrit = maxMemUtilCrit
        self.perfGainGrav2Crit = perfGainGrav2Crit
        self.isMaximizeCpuUtil = isMaximizeCpuUtil
        self.isMaximizeMemUtil = isMaximizeMemUtil

    # get optimized vCPU count
    @staticmethod
    def getVcpuOptimization(
        recoInstance,
        overProvInstance,
        overProvInstCnt,
        perfGainGrav2Crit,
        isMaximizeCpuUtil,
        maxCpuUtilCrit,
        metricType,
    ):
        logger.debug("in getVcpuOptimization")

        needToMaxCpuUtil = isMaximizeCpuUtil

        currVcpuCnt = int(overProvInstance.vcpus)
        currVcpuUtil = float(overProvInstance.cpuUtil)
        recoVcpuCnt = int(recoInstance.vcpuCntPerInstance)

        # for reco instance that are burstable, we shouldn't scale up/down
        # utilization of reco instance's utilization based on the current instance's
        # max utilization metric, as burstable are not expected to operate continuously
        # at max
        if metricType == appCommon.max_metric and recoInstance.instanceType.startswith("t4"):
            scaledCpuUtil = float(
                recoInstance.projectedVcpuUtil)
            needToMaxCpuUtil = False
        else:
            # calc cpu util corresponding to the recommended cpu count
            if currVcpuCnt == recoVcpuCnt:
                scaledCpuUtil = currVcpuUtil
            else:
                vcpuCntDiff = currVcpuCnt - \
                    recoVcpuCnt if currVcpuCnt > recoVcpuCnt else recoVcpuCnt - currVcpuCnt
                percentVcpuDiff = vcpuCntDiff / \
                    recoVcpuCnt if currVcpuCnt > recoVcpuCnt else vcpuCntDiff / currVcpuCnt
                scaledCpuUtil = currVcpuUtil * \
                    (1 + percentVcpuDiff) if currVcpuCnt > recoVcpuCnt else currVcpuUtil / \
                    (1 + percentVcpuDiff)

        scaledCpuCnt = recoVcpuCnt * overProvInstCnt

        # if input criteria was to maximize cpu utilization, only then scale/adjust the util further and derive corresponding cpu count
        if needToMaxCpuUtil:
            # compare scaledCpuUtil against maxCpuUtilCrit in order to adjust the recoVcpuCnt
            # such that new Vcpu count corresponds with the diff in utilization

            # calculate the current cpu used
            currRequiredVcpuPerRecoInstance = float(
                scaledCpuUtil * recoVcpuCnt)

            # calculate cpu needed for maxCpuUtilCrit
            requiredVcpuPerRecoForMaxUtil = (
                maxCpuUtilCrit * currRequiredVcpuPerRecoInstance
            ) / scaledCpuUtil

            # calculate total cpu usage across all instances
            requiredTotalVcpu = currRequiredVcpuPerRecoInstance * overProvInstCnt

            newInstCnt = requiredTotalVcpu / requiredVcpuPerRecoForMaxUtil

            logger.debug("newInstCnt = %f, overProvInstCnt = %d",
                         newInstCnt, overProvInstCnt)

            # vcpus corresponding to newInstCnt
            scaledCpuCnt = newInstCnt * recoVcpuCnt

            scaledCpuUtil = maxCpuUtilCrit

        # apply the Grav2 perf improvements from input criteria to the vcpu count
        # scaledCpuCnt = scaledCpuCnt * (100 / (100 + perfGainGrav2Crit))
        scaledCpuCnt = scaledCpuCnt / (1 + (perfGainGrav2Crit/100))

        logger.debug("scaledCpuCnt with Grav2 benefit = %f", scaledCpuCnt)

        data = {}
        data[appCommon.totalVcpus_FN] = scaledCpuCnt
        data[appCommon.vcpuUtil_FN] = scaledCpuUtil

        return data

    # get optimized memory

    @staticmethod
    def getMemOptimization(
        recoInstance,
        overProvInstance,
        overProvInstCnt,
        perfGainGrav2Crit,
        isMaximizeMemUtil,
        maxMemUtilCrit,
        metricType
    ):
        logger.debug("in getMemOptimization")

        isRecoInstanceBurstable = recoInstance.instanceType.startswith("t4")

        overProvInstanceMem, memUnit = re.search(
            "(.*)\s+(.*)", overProvInstance.mem).group(1, 2)
        overProvMemPerInstance = float(overProvInstanceMem)

        recoMem, recoMemUnit = re.search(
            "(.*)\s+(.*)", recoInstance.memPerInstance).group(1, 2)
        recoMemPerInstance = float(recoMem)

        currMemUtil = float(
            overProvInstance.memUtil) if overProvInstance.memUtil != "" else ""

        # for reco instance that are burstable, we shouldn't scale up/down
        # utilization of reco instance's utilization based on the current instance's
        # max utilization metric, as burstable are not expected to operate continuously
        # at max
        canMaxMemUtil = True
        if metricType == appCommon.max_metric and isRecoInstanceBurstable:
            scaledMemUtil = float(recoInstance.projectedMemUtil)
            canMaxMemUtil = False
        else:
            # calc recommended resource util based on the new resource size and old resource size
            if overProvMemPerInstance == recoMemPerInstance:
                scaledMemUtil = currMemUtil
            else:
                memDiff = overProvMemPerInstance - \
                    recoMemPerInstance if overProvMemPerInstance > recoMemPerInstance else recoMemPerInstance - \
                    overProvMemPerInstance
                percentMemDiff = memDiff / \
                    recoMemPerInstance if overProvMemPerInstance > recoMemPerInstance else memDiff / \
                    overProvMemPerInstance
                scaledMemUtil = currMemUtil * \
                    (1 + percentMemDiff) if overProvMemPerInstance > recoMemPerInstance else currMemUtil / \
                    (1 + percentMemDiff)

        scaledMem = recoMemPerInstance * overProvInstCnt

        # if input criteria was to maximize cpu utilization, only then scale/adjust the util further and derive corresponding cpu count
        if isMaximizeMemUtil and canMaxMemUtil:
            # compare scaledCpuUtil against maxCpuUtilCrit in order to adjust the recoVcpuCnt
            # such that new Vcpu count corresponds with the diff in utilization
            if scaledMemUtil < maxMemUtilCrit:
                logger.debug("scaledMemUtil %f lesser than maxMemUtilCrit %d ",
                             scaledMemUtil, maxMemUtilCrit)

                # calculate the current cpu used
                requiredMemForScaledMemUtilPerRecoInstance = float(
                    scaledMemUtil * recoMemPerInstance
                )

                # calculate cpu needed for maxCpuUtilCrit
                requiredMemPerRecoForMaxUtil = (
                    maxMemUtilCrit * requiredMemForScaledMemUtilPerRecoInstance
                ) / scaledMemUtil

                # calculate total cpu usage across all instances
                requiredTotalMem = (
                    requiredMemForScaledMemUtilPerRecoInstance * overProvInstCnt
                )

                newInstCnt = requiredTotalMem / requiredMemPerRecoForMaxUtil

                # mem corresponding to newInstCnt
                scaledMem = newInstCnt * recoMemPerInstance

                scaledMemUtil = maxMemUtilCrit

            else:
                # currently not handling scenario when scaledCpuUtil > maxCpuUtilCrit
                logger.debug("scaledMemUtil %f equal to or greater than maxMemUtilCrit %d",
                             scaledMemUtil, maxMemUtilCrit)

                scaledMem = overProvInstCnt * recoMemPerInstance

        # apply the Grav2 perf improvements from input criteria to the vcpu count
        # scaledMem = scaledMem * (100 / (100 + perfGainGrav2Crit))
        scaledMem = scaledMem / (1 + (perfGainGrav2Crit/100))

        logger.debug("scaledMem with Grav2 benefit = %f", scaledMem)

        data = {}
        data[appCommon.totalMem_FN] = scaledMem
        data[appCommon.memUtilization_FN] = scaledMemUtil

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

    def optimizeResourcesForInstance(
        self,
        recoInstance,
        overProvInstance
    ):
        logger.debug("in optimizeResourcesForInstance")

        data = {}

        recoVcpuCntPerInstance = int(recoInstance.vcpuCntPerInstance)

        recoMem, recoMemUnit = re.search(
            "(.*)\s+(.*)", recoInstance.memPerInstance).group(1, 2)
        recoMemPerInstance = float(recoMem)

        currMemUtil = float(
            overProvInstance.memUtil) if overProvInstance.memUtil != "" else ""

        # optimize for vCPU
        vcpuOptResult = OverProvInstanceOptimizer.getVcpuOptimization(
            recoInstance,
            overProvInstance,
            self.overProvInstCnt,
            self.perfGainGrav2Crit,
            self.isMaximizeCpuUtil,
            self.maxCpuUtilCrit,
            self.metricType,
        )

        data[appCommon.recoProjectedMaxVcpuUtil_FN] = "{:.2f}".format(
            vcpuOptResult[appCommon.vcpuUtil_FN]) + " %"

        data[appCommon.recoProjectedMaxMemUtilTxt] = appCommon.notAvailTxt
        requiredTotalVcpuCnt = vcpuOptResult[appCommon.totalVcpus_FN]

        # optimize for memory ONLY if the current instance's memory utilization is available
        if currMemUtil != "":
            memOptResult = OverProvInstanceOptimizer.getMemOptimization(
                recoInstance,
                overProvInstance,
                self.overProvInstCnt,
                self.perfGainGrav2Crit,
                self.isMaximizeMemUtil,
                self.maxMemUtilCrit,
                self.metricType
            )

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

        perfRisk = recoInstance.perfRisk
        recoPerfRisk = str(
            perfRisk) if perfRisk != None else appCommon.notApplicableTxt
        data[appCommon.recoPerfRisk_FN] = OverProvInstanceOptimizer.getPerfRiskLevel(
            recoPerfRisk)

        return data

    def computeSavingsForOverProvInstance(
        self,
        overProvInstance,
        recoList
    ):
        logger.debug("in computeSavingsForOverProvInstance")

        data = {}

        currMem, memUnit = re.search(
            "(.*)\s+(.*)", overProvInstance.mem).group(1, 2)

        data[appCommon.overProvInstanceArn_FN] = overProvInstance.instanceArn
        data[appCommon.overProvInstanceName_FN] = overProvInstance.instanceName
        data[appCommon.overProvInstanceType_FN] = overProvInstance.instanceType
        data[appCommon.tag_FN] = overProvInstance.tag

        data[appCommon.cpuUtilizationNumeric_FN] = float(
            overProvInstance.cpuUtil)
        data[appCommon.cpuUtilization_FN] = "{:.2f}".format(
            float(overProvInstance.cpuUtil)) + " %"

        data[appCommon.memUtilization_FN] = "{:.2f}".format(
            float(overProvInstance.memUtil)) + " %" \
            if (overProvInstance.memUtil != None and overProvInstance.memUtil != "") \
            else appCommon.notAvailTxt

        # for full detail report, add each reco for the overprovisioned instance

        data[appCommon.currentTotalVcpus_FN] = int(
            overProvInstance.vcpus) * self.overProvInstCnt
        data[appCommon.currentTotalMem_FN] = str(
            float(currMem) * self.overProvInstCnt) + " " + memUnit
        data[appCommon.currentTotalInstances_FN] = self.overProvInstCnt
        currentTotalMonthlyCost = self.overProvInstCnt * \
            float(overProvInstance.hourlyOnDemandPrice) * 730
        data[appCommon.currentTotalMonthlyCost_FN] = "${:0,.0f}".format(
            math.ceil(currentTotalMonthlyCost)
        )

        optimizedFleetRecoList = []

        # process each instance recommended by Compute Optimizer
        for recoInstance in recoList:

            optimizedFleetReco = self.optimizeResourcesForInstance(
                recoInstance,
                overProvInstance
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

    def optimizeComputeForSavings(self):
        logger.debug("in optimizeComputeForSavings")

        # Read csv from S3
        s3_data = appCommon.s3.get_object(Bucket=self.s3Bucket, Key=self.s3Key)

        optimizationResult = []

        for record in csv.DictReader(codecs.getreader("utf-8")(s3_data["Body"])):

            overProvInstance = appCommon.OverProvInstance(
                record, self.metricType)

            if overProvInstance.finding == "OVER_PROVISIONED" and overProvInstance.instanceArn == self.overProvInstArn:
                recoList = []
                recoCnt = int(overProvInstance.recommendationCnt)
                i = 1
                while i <= recoCnt:
                    recoList.append(appCommon.RecommendedInstance(
                        record, str(i), self.metricType))
                    i += 1

                optimizationResult.append(
                    self.computeSavingsForOverProvInstance(
                        overProvInstance,
                        recoList)
                )

                # break from loop since we are not interested in optimizing beyond the selected instance
                break

        return optimizationResult
