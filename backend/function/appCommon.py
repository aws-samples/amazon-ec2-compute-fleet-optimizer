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

import boto3

#initialize s3 client 
s3 = boto3.client("s3")

burstableBaselineUtil = {
    "t4g.nano": 5,
    "t4g.micro": 10,
    "t4g.small": 20,
    "t4g.medium": 20,
    "t4g.large": 30,
    "t4g.xlarge": 40,
    "t4g.2xlarge": 40,
}

max_metric = "max"
avg_metric = "avg"

cpu_util_delta_with_fleet_avg = 5

utilMetricsText = "utilizationMetrics_"
projUtilMetricsText = "_projectedUtilizationMetrics_"
recommendOptionsTxt = "recommendationOptions_"
overProvInstanceArn_FN = "overProvInstanceArn"
overProvInstanceName_FN = "overProvInstanceName"
overProvInstanceType_FN = "overProvInstanceType"
overProvInstanceCount_FN = "overProvInstanceCount"
maxCpuUtilCriteria_FN = "maxCpuUtilCriteria"
maxMemUtilCriteria_FN = "maxMemUtilCriteria"
perfGainedGrav2Criteria_FN = "perfGainedGrav2Criteria"
isMaximizeCpuUtilCrit_FN = "isMaximizeCpuUtilCrit"
isMaximizeMemUtilCrit_FN = "isMaximizeMemUtilCrit"
instanceTypeTxt = "_instanceType"
vcpusSuffix = "_vcpus"
memSuffix = "_memory"
currentVcpus_FN = "current_vcpus"
totalVcpus_FN = "total_vcpus"
currentMem_FN = "current_memory"
avgFleetVCpuUtil_FN = "avgFleetVCpuUtil"
totalFleetInstCnt_FN = "totalFleetInstCnt"
totalVCpuUtil_FN = "totalVCpuUtil"
totalInstCnt_FN = "totalInstCnt"
currentInstanceType_FN = "currentInstanceType"
instanceArn_FN = "instanceArn"
instanceName_FN = "instanceName"
cpuUtilizationNumeric_FN = "cpuUtilizationNumeric"
memUtilization_FN = "memUtilization"
cpuUtilization_FN = "cpuUtilization"
currOnDemandPrice_FN = "current_onDemandPrice"
onDemandPriceTxt = "_onDemandPrice"
totalMem_FN = "total_mem"
perfRiskTxt = "_performanceRisk"
vcpuUtil_FN = "vcpuUtil"
recoInstanceType_FN = "recoInstanceType"
recoTotalMonthlyCost_FN = "recoTotalMonthlyCost"
recoPriceDiff_FN = "recoPriceDiff"
recoPriceDiffPercent_FN = "recoPriceDiffPercent"
currentTotalMonthlyCost_FN = "currentTotalMonthlyCost"
currentTotalInstances_FN = "currentTotalInstances"
currentTotalVcpus_FN = "currentTotalVcpus"
currentTotalMem_FN = "currentTotalMem"
recoPerfRisk_FN = "recoPerfRisk"
recoTotalVcpus_FN = "recoTotalVcpus"
recoTotalMem_FN = "recoTotalMem"
recoTotalInstances_FN = "recoTotalInstances"
notAvailTxt = "not available"
recoProjectedMaxMemUtilTxt = "recoProjectedMaxMemUtil"
recoProjectedMaxVcpuUtil_FN = "recoProjectedMaxVcpuUtil"
recommendationsCnt_FN = "recommendations_count"
isCpuUtilWithin5Percent_FN = "isCpuUtilWithin5Percent"
notApplicableTxt = "NA"
tag_FN = "tag"
finding_FN = "finding"
recommendations_FN = "recos"


def getTextMaxOrAvg(resourceType, utilMetricType):
    if utilMetricType == max_metric:
        return resourceType + "_MAXIMUM"
    else:
        return resourceType + "_AVERAGE"


def getTextVcpuMaxOrAvg(utilMetricType):
    return getTextMaxOrAvg("CPU", utilMetricType)


def getTextMemMaxOrAvg(utilMetricType):
    return getTextMaxOrAvg("MEMORY", utilMetricType)


def getCurrInstanceVcpuUtilFN(utilMetricType):
    return utilMetricsText + \
        getTextVcpuMaxOrAvg(utilMetricType)


def getCurrInstanceMemUtilFN(utilMetricType):
    return utilMetricsText + \
        getTextMemMaxOrAvg(utilMetricType)


def getRecoProjVcpuUtilFN(recoIdx, utilMetricType):
    return recommendOptionsTxt + recoIdx + \
        projUtilMetricsText + getTextVcpuMaxOrAvg(utilMetricType)


def getRecoProjMemUtilFN(recoIdx, utilMetricType):
    return recommendOptionsTxt + recoIdx + \
        projUtilMetricsText + getTextMemMaxOrAvg(utilMetricType)


def getRecoInstanceTypeFN(recoIdx):
    return recommendOptionsTxt + recoIdx + instanceTypeTxt


def getRecoVcpuCntFN(recoIdx):
    return recommendOptionsTxt + recoIdx + vcpusSuffix


def getRecoMemFN(recoIdx):
    return recommendOptionsTxt + recoIdx + memSuffix


def getRecoPerfRiskFN(recoIdx):
    return recommendOptionsTxt + recoIdx + perfRiskTxt


def getRecoOnDemandPriceField(recoIdx):
    return recommendOptionsTxt + \
        recoIdx + onDemandPriceTxt


class OverProvInstance():

    def __init__(self, record, metricType):
        self.vcpus = record[currentVcpus_FN]
        self.mem = record[currentMem_FN]
        self.tag = record[tag_FN]
        self.finding = record[finding_FN]
        self.recommendationCnt = record[recommendationsCnt_FN]
        self.cpuUtil = record[getCurrInstanceVcpuUtilFN(metricType)]
        self.memUtil = record[getCurrInstanceMemUtilFN(metricType)]
        self.instanceName = record[instanceName_FN]
        self.instanceArn = record[instanceArn_FN]
        self.instanceType = record[currentInstanceType_FN]
        self.hourlyOnDemandPrice = record[currOnDemandPrice_FN]


class RecommendedInstance():

    def __init__(self, record, recordIdx, metricType):
        self.projectedVcpuUtil = record[getRecoProjVcpuUtilFN(
            recordIdx, metricType)]
        self.projectedMemUtil = record[getRecoProjMemUtilFN(
            recordIdx, metricType)]
        self.instanceType = record[getRecoInstanceTypeFN(recordIdx)]
        self.vcpuCntPerInstance = int(
            record[getRecoVcpuCntFN(recordIdx)])
        self.memPerInstance = record[getRecoMemFN(recordIdx)]
        self.perfRisk = record[getRecoPerfRiskFN(recordIdx)]
        self.hourlyOnDemandPrice = record[getRecoOnDemandPriceField(
            recordIdx)]
