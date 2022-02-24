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
        Review the table below for the recommended EC2 instance(s) for EC2
        compute fleet tagged '{{ this.fleetId }}'
      </p>
    </div>
    <div v-if="loading" class="loader" />
    <br />
    <div v-if="!loading">
      <div v-for="item in overProvInstanceDetails" :key="item">
        {{ item.name }}:
        <span style="font-color: #add8e6">{{ item.value }}</span>
      </div>
      <br />
      <v-data-table
        :headers="headers"
        :items="instances"
        item-key="recoInstanceType"
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
      headers: [
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
        { text: 'Performance Risk', value: 'recoPerfRisk', width: '' },
      ],
      overProvInstanceDetails: [],
      instances: [],
      loading: false,
    };
  },
  async created() {
    console.log('In created');
    this.loading = true;

    this.fleetId = AmplifyStore.state.overProvEc2.fleetId;
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
        s3BucketName: AmplifyStore.state.computeOptReport.s3Bucket,
        s3KeyName: AmplifyStore.state.computeOptReport.s3ObjKey,
        requestType: 'optimizeComputeFleet',
        overProvInstanceType: AmplifyStore.state.overProvEc2.instanceType,
        overProvInstanceArn: AmplifyStore.state.overProvEc2.instanceArn,
        overProvInstanceName: AmplifyStore.state.overProvEc2.instanceName,
        overProvInstanceCount:
          AmplifyStore.state.overProvEc2.instanceTotalFleetInstCnt,
        maxCpuUtilCriteria: AmplifyStore.state.optimizeCrit.maxCpuUtilCriteria,
        maxMemUtilCriteria: AmplifyStore.state.optimizeCrit.maxMemUtilCriteria,
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
      console.debug(AmplifyStore.state.sessionCtx, this.$apiPath);
      AmplifyStore.state.sessionCtx.apigClient
        .invokeApi(
          pathParams,
          this.$apiPath,
          method,
          additionalParams,
          postData
        )
        .then((res) => {
          console.log('RESPONSE RECEIVED: ', res);
          // handle success
          this.loading = false;
          for (let i in res.data) {
            if (i == 0) {
              this.populateOverProvInstanceDetails(
                'CPU Util % value used for current fleet',
                res.data[i]['cpuUtilization']
              );
              this.populateOverProvInstanceDetails(
                'Memory Util % value used for current fleet',
                res.data[i]['memUtilization']
              );
              this.populateOverProvInstanceDetails(
                'Current fleet EC2 instance type',
                res.data[i]['overProvInstanceType']
              );
              this.populateOverProvInstanceDetails(
                'Current fleet total vCPU',
                res.data[i]['currentTotalVcpus']
              );
              this.populateOverProvInstanceDetails(
                'Current fleet total memory',
                res.data[i]['currentTotalMem']
              );
              this.populateOverProvInstanceDetails(
                'Current fleet total # EC2 instances',
                res.data[i]['currentTotalInstances']
              );
              this.populateOverProvInstanceDetails(
                'Current fleet Monthly Cost',
                res.data[i]['currentTotalMonthlyCost']
              );
            }

            // populate the table row here
            this.instances = res.data[i]['recos'];
          }
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
