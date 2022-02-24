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
      <p class="h2prompt">Enter your compute fleet recommendations criteria</p>
    </div>
    <div class="row mt-2">
      <form class="form-wrapper">
        <div class="form-group">
          <label class="font-weight-bold">Current # of EC2 instances</label>
          <div class="col-md-4">
            <input
              id="overProvCnt"
              size="120"
              autocomplete="on"
              v-model="overProvInstanceCount"
              type="number"
              class="form-control"
              placeholder="Numeric input"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label class="font-weight-bold">Target CPU Utilization %</label>
          <div class="col-md-4">
            <input
              id="cpuUtil"
              size="120"
              autocomplete="on"
              v-model="maxCpuUtilCriteria"
              type="number"
              class="form-control"
              required
              margin="2px"
            />
          </div>
        </div>
        <div class="form-group">
          <label class="font-weight-bold">Target Memory Utilization %</label>
          <div class="col-md-4">
            <input
              id="memUtil"
              size="120"
              autocomplete="on"
              v-model="maxMemUtilCriteria"
              type="number"
              class="form-control"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label class="font-weight-bold"
            >Estimated Graviton2 Performance Gain %</label
          >
          <div class="col-md-4">
            <input
              id="grav2Gain"
              size="120"
              autocomplete="on"
              v-model="perfGainedGrav2Criteria"
              type="number"
              class="form-control"
              required
            />
          </div>
        </div>
      </form>
    </div>
    <div class="row mt-2">
      <button
        v-if="isSubmitable"
        class="btn btn-primary btn-block mt-3"
        v-on:click="processSubmit()"
      >
        Next
      </button>
    </div>
  </div>
</template>
<script>
import AmplifyStore from '../store/store';

export default {
  name: 'OptimizeCriteria',
  data() {
    return {
      overProvInstanceCount: Number,
      maxCpuUtilCriteria: 80,
      maxMemUtilCriteria: 70,
      perfGainedGrav2Criteria: 20,
      isMaximizeCpuUtilCriteria: true,
      isMaximizeMemUtilCriteria: true,
      isDisableSubmit: false,
    };
  },
  created() {
    console.log('In created');

    this.overProvInstanceCount =
      AmplifyStore.state.overProvEc2.instanceTotalFleetInstCnt;
  },
  methods: {
    processSubmit() {
      var optimizeCriteria = {};
      optimizeCriteria.maxCpuUtilCriteria = this.maxCpuUtilCriteria;
      optimizeCriteria.maxMemUtilCriteria = this.maxMemUtilCriteria;
      optimizeCriteria.perfGainedGrav2Criteria = this.perfGainedGrav2Criteria;
      optimizeCriteria.isMaximizeCpuUtilCriteria =
        this.isMaximizeCpuUtilCriteria;
      optimizeCriteria.isMaximizeMemUtilCriteria =
        this.isMaximizeMemUtilCriteria;

      AmplifyStore.commit('setOptimizeCriteria', optimizeCriteria);

      this.$router.push({
        path: 'recolist',
      });
    },
    isSubmitable: function () {
      return !this.isDisableSubmit;
    },
  },
};
</script>
