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
        Select a EC2 instance from this list of Over-Provisioned instances in
        the fleet. Choose one with a CPU Utilization that closely matches the
        Average CPU Utilization of its fleet.
      </p>
    </div>
    <br />
    <div>
      <form>
        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="instances"
          item-key="overProvInstanceArn"
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
  </div>
</template>
<script>
import AmplifyStore from '../store/store';

export default {
  name: 'overprovinstances',

  data() {
    return {
      selected: [],
      headers: [
        { text: 'Instance Arn', value: 'overProvInstanceArn', width: '20%' },
        { text: 'Instance Name', value: 'overProvInstanceName', width: '15%' },
        { text: 'Instance Type', value: 'overProvInstanceType', width: '10%' },
        { text: 'CPU Utilization', value: 'cpuUtilization', width: '' },
        {
          text: 'Avg. Fleet CPU Utilization',
          value: 'avgFleetVCpuUtil',
          width: '',
        },
        { text: 'Total Fleet Size', value: 'totalFleetInstCnt', width: '' },
        { text: 'Memory Utilization', value: 'memUtilization', width: '' },
      ],
      instances: [],
      selectedInstanceType: '',
      selectedInstanceName: '',
      isDisableSubmit: false,
    };
  },
  async created() {
    console.log('In created');
    this.fleetId = AmplifyStore.state.overProvFleet.fleetId;
    this.instances = AmplifyStore.state.overProvFleet.instances;
  },
  methods: {
    processSubmit() {
      var selectedEc2 = {};
      selectedEc2.selectedInstanceArn = this.selected[0].overProvInstanceArn;
      selectedEc2.selectedInstanceType = this.selected[0].overProvInstanceType;
      selectedEc2.selectedInstanceName = this.selected[0].overProvInstanceName;
      selectedEc2.selectedInstanceTotalFleetInstCnt =
        this.selected[0].totalFleetInstCnt;
      selectedEc2.fleetId = this.selected[0].tag;

      AmplifyStore.commit('setOverProvEc2', selectedEc2);

      this.$router.push({
        path: 'optimizecriteria',
      });
    },
  },
};
</script>
