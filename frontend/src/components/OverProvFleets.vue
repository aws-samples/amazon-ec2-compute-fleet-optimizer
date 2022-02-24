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
        Select a compute fleet below and hit Next. These fleets contain one or
        more over-provisioned EC2 instances, as identified in the export file
        from AWS Compute Optimizer. We'll attempt to optimize the compute
        instances in this fleet in the next step.
      </p>
    </div>
    <div v-if="loading" class="loader"></div>
    <br />
    <div v-if="!errorText && !loading">
      <form>
        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="fleetTblData"
          item-key="tag"
          class="elevation-1"
          :single-select="true"
          show-select
        />
        <div id="form-response"></div>
        <button
          :disabled="this.selected.length == 0"
          class="btn btn-primary btn-block mt-3"
          v-on:click="processSubmit()"
        >
          Next
        </button>
      </form>
    </div>
    <div v-if="errorText" style="color: red">ERROR: {{ this.errorText }}</div>
  </div>
</template>
<script>
import AmplifyStore from '../store/store';

export default {
  name: 'overprovfleets',

  data() {
    return {
      selected: [],
      headers: [
        { text: 'Fleet Id', value: 'tag', width: '' },
        {
          text: 'Avg. Fleet CPU Utilization',
          value: 'avgFleetVCpuUtil',
          width: '',
        },
        { text: 'Total Fleet Size', value: 'totalFleetInstCnt', width: '' },
      ],
      fleetData: {},
      fleetTblData: [],
      errorText: null,
      isServerRespEmpty: false,
      isFleetTagMissing: false,
      loading: false,
    };
  },
  async created() {
    console.log('In created');

    this.loading = true;

    this.postData();
  },
  methods: {
    processSubmit() {
      var overProvFleet = {};
      overProvFleet.fleetId = this.selected[0].tag;
      overProvFleet.fleetInstances = this.fleetData[this.selected[0].tag];

      AmplifyStore.commit('setOverProvFleet', overProvFleet);

      this.$router.push({
        path: 'overprovinstances',
      });
    },
    async postData() {
      console.log(AmplifyStore.state.computeOptReport);

      var postData = {
        s3BucketName: AmplifyStore.state.computeOptReport.s3Bucket,
        s3KeyName: AmplifyStore.state.computeOptReport.s3ObjKey,
        requestType: 'aggregateFleetLevelStats',
      };
      var pathParams = {};
      var method = 'POST';
      var additionalParams = {};
      console.debug(AmplifyStore.state.sessionCtx);
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

          var fleetData = {};
          var tableData = [];
          var fleetIdx = 0;

          if (res.data.length == 0) {
            this.isServerRespEmpty = true;
            this.errorText =
              "The provided EC2 recommendations from Compute Optimizer doesn't have any EC2 instance \
              record that is marked as Over-Provisioned. This tool currently supports optimizing for \
              just Over-Provisioned EC2 instances.";

            return;
          }
          for (let i in res.data) {
            var tag = res.data[i]['tag'];
            var avgFleetVcpuUtil = res.data[i]['avgFleetVCpuUtil'];

            if (tag == '' || avgFleetVcpuUtil == 'not available') {
              continue;
            }
            var fleetInstances = fleetData[tag];
            if (fleetInstances == null) {
              fleetInstances = [];
              fleetData[tag] = fleetInstances;

              var fleetSummary = {};
              fleetSummary['tag'] = res.data[i]['tag'];
              fleetSummary['avgFleetVCpuUtil'] =
                res.data[i]['avgFleetVCpuUtil'];
              fleetSummary['totalFleetInstCnt'] =
                res.data[i]['totalFleetInstCnt'];

              tableData[fleetIdx] = fleetSummary;
              fleetIdx++;
            }

            fleetInstances.push(res.data[i]);
          }

          if (tableData.length == 0) {
            this.isFleetTagMissing = true;
            this.errorText =
              "The provided EC2 recommendations from Compute Optimizer doesn't have any EC2 instance record that is tagged with its fleet id. Please try again after ensuring the ec2 instances in there are tagged with the corresponding fleet/workload id !!";
            return;
          }

          this.fleetTblData = tableData;
          this.fleetData = fleetData;
        })
        .catch((err) => {
          console.error('Error in request handling: ', err);
          this.loading = false;
          this.errorText = 'Server returned an error: ' + err.message;
        });
    },
  },
};
</script>
