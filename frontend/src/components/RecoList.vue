/*! Copyright Amazon.com Inc. or its affiliates. SPDX-License-Identifier: MIT No
Attribution(MIT-0) Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom
the Software is furnished to do so. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT
WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE. */

<template>
  <div class="container">
    <div class="row mt-2">
      <p class="h1title">Fleet Optimizer with Graviton</p>
    </div>
    <div class="row mt-2">
      <p class="h2prompt">
        Review the table below for the recommended EC2 instance type(s) for
        compute fleet tagged '{{ this.fleetId }}'
      </p>
    </div>
    <div v-if="loading" class="loader" />
    <br />

    <div v-if="!loading">
      <p class="h3prompt">Recommendations and cost difference</p>
      <v-data-table
        :headers="recommendationHeaders"
        :items="recoInstances"
        item-key="recoInstanceType"
        hide-default-footer
        class="elevation-1"
      />

      <br />
      <br />
      <p class="h3prompt">Current Fleet instance type and cost</p>
      <v-data-table
        :headers="headers"
        :items="instances"
        item-key="overProvInstanceType"
        hide-default-footer
        class="elevation-1"
      />

      <!--table class="table table-striped table-hover mt-2"-->
    </div>
  </div>
</template>
<script>
import AmplifyStore from '../store/store';

export default {
  name: 'RecoList',

  data() {
    return {
      fleetId: null,
      headers: [
        {
          text: 'Current Instance Type',
          value: 'overProvInstanceType',
          width: '12%',
        },
        {
          text: 'Monthly Cost',
          value: 'currentTotalMonthlyCost',
          width: '12%',
        },
        {
          text: 'Total # Instances',
          value: 'currentTotalInstances',
          width: '',
        },
        { text: 'Total vCPU', value: 'currentTotalVcpus', width: '' },
        { text: 'Total Memory', value: 'currentTotalMem', width: '' },
        {
          text: 'Fleet CPU Utilization',
          value: 'fleetAvgCpuUtil',
          width: '',
        },
        {
          text: 'Fleet Memory Utilization',
          value: 'fleetAvgMemUtil',
          width: '',
        },
      ],
      recommendationHeaders: [
        {
          text: 'Recommended Instance Type',
          value: 'recoInstanceType',
          width: '12%',
        },
        {
          text: 'Estimated Monthly Cost',
          value: 'recoTotalMonthlyCost',
          width: '12%',
        },
        {
          text: 'Cost Difference %',
          value: 'recoPriceDiffPercent',
          width: '12%',
        },
        { text: 'Cost Difference', value: 'recoPriceDiff', width: '' },
        { text: 'Performance Risk', value: 'recoPerfRisk', width: '' },
        { text: 'Total # Instances', value: 'recoTotalInstances', width: '' },
        { text: 'Total vCPU', value: 'recoTotalVcpus', width: '' },
        { text: 'Total Memory', value: 'recoTotalMem', width: '' },
        {
          text: 'Projected CPU Utilization',
          value: 'recoProjectedMaxVcpuUtil',
          width: '',
        },
        {
          text: 'Projected Memory Utilization',
          value: 'recoProjectedMaxMemUtil',
          width: '',
        },
      ],
      overProvInstanceDetails: [],
      instances: [],
      recoInstances: [],
      fleetAvgCpuUtil: 0,
      fleetMemCpuUtil: 0,
      loading: false,
    };
  },
  async created() {
    console.log('In created');
    this.loading = true;

    this.fleetId = AmplifyStore.state.overProvFleet.fleetId;
    this.fleetAvgCpuUtil = AmplifyStore.state.overProvFleet.fleetAvgCpuUtil;
    this.fleetAvgMemUtil = AmplifyStore.state.overProvFleet.fleetAvgMemUtil;

    this.postData();
  },
  methods: {
    populateOverProvInstanceDetails(fieldName, fieldValue) {
      this.overProvInstanceDetails.push({
        name: fieldName,
        value: fieldValue,
      });
    },
    async postData() {
      console.log(AmplifyStore.state.computeOptReport);
      console.log(AmplifyStore.state.overProvEc2);
      console.log(AmplifyStore.state.optimizeCrit);

      var postData = {
        requestType: 'optimizeComputeFleet',
        s3BucketName: AmplifyStore.state.computeOptReport.s3Bucket,
        s3KeyName: AmplifyStore.state.computeOptReport.s3ObjKey,
        tag: this.fleetId,
        fleetInstanceType: AmplifyStore.state.overProvFleet.fleetInstanceType,
        maxCpuUtilCriteria: AmplifyStore.state.optimizeCrit.maxCpuUtilCriteria,
        maxMemUtilCriteria: AmplifyStore.state.optimizeCrit.maxMemUtilCriteria,
        hasGravitonPerfGainCriteria:
          AmplifyStore.state.optimizeCrit.hasGravitonPerfGainCriteria,
        perfGainedGrav2Criteria:
          AmplifyStore.state.optimizeCrit.perfGainedGrav2Criteria,
        isMaximizeCpuUtilCrit:
          AmplifyStore.state.optimizeCrit.isMaximizeCpuUtilCriteria,
        isMaximizeMemUtilCrit:
          AmplifyStore.state.optimizeCrit.isMaximizeMemUtilCriteria,
      };
      var pathParams = {};
      var method = 'POST';
      var additionalParams = {};
      console.debug(
        AmplifyStore.state.sessionCtx,
        this.$pricePerfOptimizeApiPath
      );
      AmplifyStore.state.sessionCtx.apigClient
        .invokeApi(
          pathParams,
          this.$pricePerfOptimizeApiPath,
          method,
          additionalParams,
          postData
        )
        .then((res) => {
          console.log('RESPONSE RECEIVED: ', res);
          // handle success
          this.loading = false;

          var currentFleetData = {};

          currentFleetData['fleetAvgCpuUtil'] = this.fleetAvgCpuUtil + '%';

          currentFleetData['fleetAvgMemUtil'] = this.fleetAvgMemUtil + '%';

          currentFleetData['overProvInstanceType'] =
            res.data['overProvInstanceType'];

          currentFleetData['currentTotalVcpus'] = res.data['currentTotalVcpus'];

          currentFleetData['currentTotalMem'] = res.data['currentTotalMem'];

          currentFleetData['currentTotalInstances'] =
            res.data['currentTotalInstances'];

          currentFleetData['currentTotalMonthlyCost'] =
            res.data['currentTotalMonthlyCost'];

          this.instances = [];
          this.instances.push(currentFleetData);
          // populate the table row here
          this.recoInstances = res.data['recos'];

          console.log('Populated table', res.data);
        })
        .catch((err) => {
          console.log(err.response);
          // handle error
          console.error('Error requesting ride: ', err);
          this.loading = false;
          alert('An error occured when requesting your unicorn:\n' + err);
        });
    },
  },
};
</script>
