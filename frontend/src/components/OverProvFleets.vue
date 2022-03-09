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
      <div class="col-md-12">
        <p class="h2prompt">
          The table shows data synthesized from the uploaded Compute Optimizer
          report. Take a look at the key attributes of your compute fleets,
          especially the EC2 instance type, average CPU and Memory utilization,
          based on which you can decide which fleet to choose for optimization.
        </p>
        <p class="h2prompt">Select a compute fleet below and hit Next.</p>
      </div>
    </div>
    <div v-if="loading" class="loader"></div>
    <br />
    <div v-if="!errorText && !loading">
      <form>
        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="fleetTblData"
          item-key="tblKey"
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
import config from '../aws-exports';

export default {
  name: 'overprovfleets',

  data() {
    return {
      selected: [],
      headers: [
        { text: 'Fleet Id', value: 'tag', width: '' },
        {
          text: 'EC2 Instance Type',
          value: 'overProvInstanceType',
          width: '',
        },
        { text: 'Total Fleet Size', value: 'totalFleetInstCnt', width: '' },
        {
          text: 'Avg. Fleet CPU Utilization',
          value: 'avgFleetVCpuUtil',
          width: '',
        },
        {
          text: 'Avg. Fleet Memory Utilization',
          value: 'avgFleetMemUtil',
          width: '',
        },
      ],
      fleetTblData: [],
      errorText: null,
      isServerRespEmpty: false,
      isFleetTagMissing: false,
      loading: false,
      s3BucketName: `${config.aws_user_files_s3_bucket}`,
      s3ObjectKey: '',
    };
  },
  async created() {
    console.log('In created');

    this.loading = true;

    this.uploadImage();
  },
  methods: {
    processSubmit() {
      var overProvFleet = {};
      overProvFleet.fleetId = this.selected[0].tag;
      overProvFleet.fleetInstanceType = this.selected[0].overProvInstanceType;
      overProvFleet.fleetAvgCpuUtil = this.selected[0].avgFleetVCpuUtil.split(
        ' ',
        1
      )[0];
      let hasAvgFleetMemUtil = this.selected[0].hasAvgFleetMemUtil;
      overProvFleet.hasAvgFleetMemUtil = hasAvgFleetMemUtil;

      if (hasAvgFleetMemUtil)
        overProvFleet.fleetAvgMemUtil = this.selected[0].avgFleetMemUtil.split(
          ' ',
          1
        )[0];
      else overProvFleet.fleetAvgMemUtil = this.selected[0].avgFleetMemUtil;

      AmplifyStore.commit('setOverProvFleet', overProvFleet);

      this.$router.push({
        path: 'optimizecriteria',
      });
    },
    uploadImage: async function () {
      console.log('uploading file..........');
      console.log('Uploading: ', AmplifyStore.state.computeOptReport.image);

      var pathParams = {};
      var method = 'GET';
      var additionalParams = {};
      console.debug(AmplifyStore.state.sessionCtx);
      console.log('Get upoad urlpath ..........');

      console.log(this.$getUploadUrlApiPath);

      var response;
      try {
        response = await AmplifyStore.state.sessionCtx.apigClient.invokeApi(
          pathParams,
          this.$getUploadUrlApiPath,
          method,
          additionalParams
        );

        console.log('Response: ', response.data);

        if (!response.data.uploadURL) {
          this.isServerRespEmpty = true;
          this.errorText =
            "The provided EC2 recommendations from Compute Optimizer doesn't have any EC2 instance \
              record that is marked as Over-Provisioned. This tool currently supports optimizing for \
              just Over-Provisioned EC2 instances.";

          return;
        }

        let binary = atob(
          AmplifyStore.state.computeOptReport.image.split(',')[1]
        );
        let array = [];
        for (var i = 0; i < binary.length; i++) {
          array.push(binary.charCodeAt(i));
        }
        let blobData = new Blob([new Uint8Array(array)], {
          type: 'text/csv',
        });
        console.log('Uploading to: ', response.data.uploadURL);
        const result = await fetch(response.data.uploadURL, {
          method: 'PUT',
          body: blobData,
        });
        console.log('File upload to S3 Result: ', result);
        // Final URL for the user doesn't need the query string params
        this.uploadURL = response.data.uploadURL.split('?')[0];
        this.s3ObjectKey = response.data.photoFilename;
        // handle success
        this.postData();
      } catch (err) {
        console.error('Error in request handling: ', err);
        this.loading = false;
        this.errorText = 'Server returned an error: ' + err.message;
      }
    },
    async postData() {
      console.log(AmplifyStore.state.computeOptReport);
      var computeOptReport = {};
      computeOptReport.image = AmplifyStore.state.computeOptReport.image;
      computeOptReport.s3Bucket = this.s3BucketName;
      computeOptReport.s3ObjKey = this.s3ObjectKey;

      AmplifyStore.commit('setComputeOptReport', computeOptReport);

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
          this.$pricePerfOptimizeApiPath,
          method,
          additionalParams,
          postData
        )
        .then((res) => {
          console.log('RESPONSE RECEIVED: ', res);
          // handle success
          this.loading = false;

          var tableData = [];
          var fleetIdx = 0;

          if (res.data == null) {
            this.isServerRespEmpty = true;
            this.errorText =
              "The provided EC2 recommendations from Compute Optimizer doesn't have any EC2 instance \
              record that is marked as Over-Provisioned. This tool currently supports optimizing for \
              just Over-Provisioned EC2 instances.";

            return;
          }

          for (var fleetTag in res.data) {
            var instanceTypes = res.data[fleetTag];
            for (var instanceType in instanceTypes) {
              var fleetData = instanceTypes[instanceType];

              var fleetSummary = {};

              fleetSummary['tblKey'] = fleetTag + '-' + instanceType;
              fleetSummary['tag'] = fleetTag;
              fleetSummary['overProvInstanceType'] = instanceType;
              fleetSummary['totalFleetInstCnt'] =
                fleetData['totalFleetInstCnt'];

              fleetSummary['avgFleetVCpuUtil'] =
                parseFloat(fleetData['avgFleetVCpuUtil']).toFixed(2) + ' %';

              var hasAvgFleetMemUtil = fleetData['hasAvgFleetMemUtil'];

              fleetSummary['hasAvgFleetMemUtil'] = hasAvgFleetMemUtil;

              var fleetAvgMemUtil = hasAvgFleetMemUtil
                ? parseFloat(fleetData['avgFleetMemUtil']).toFixed(2) + ' %'
                : 'not available';
              fleetSummary['avgFleetMemUtil'] = fleetAvgMemUtil;

              tableData[fleetIdx] = fleetSummary;

              fleetIdx++;
            }
          }

          if (tableData.length == 0) {
            this.isFleetTagMissing = true;
            this.errorText =
              "The provided EC2 recommendations from Compute Optimizer doesn't \
              have any EC2 instance record that is tagged with its fleet id. \
              Please try again after ensuring the ec2 instances in there are tagged \
              with the corresponding fleet/workload id !!";

            return;
          }

          this.fleetTblData = tableData;
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
