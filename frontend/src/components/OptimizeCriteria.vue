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
      <p class="h2prompt">Enter your fleet optimization criteria</p>
    </div>
    <div class="form-group">
      <v-container>
        <div class="col-md-12">
          <div class="col-md-12">
            <input
              type="checkbox"
              v-model="hasGravitonPerfGainCriteria"
              id="accept1"
              class="form-check-input"
            />

            <label class="form-check-label h3prompt" for="accept1"
              >Apply compute performance gain with Graviton
            </label>
          </div>
          <div>
            <div class="row">
              <div
                :disabled="hasGravitonPerfGainCriteria != 1"
                class="col-md-4"
              >
                <label :disabled="hasGravitonPerfGainCriteria != 1"
                  >Estimated Graviton2 Performance Gain %</label
                >
                <input
                  size="120"
                  autocomplete="on"
                  v-model="perfGainedGrav2Criteria"
                  type="number"
                  class="form-control"
                  required
                  margin="2px"
                  :disabled="hasGravitonPerfGainCriteria != 1"
                />
              </div>
              <div class="col-md-8">
                <label
                  :disabled="hasGravitonPerfGainCriteria != 1"
                  class="text-muted helptext"
                  >Amazon Graviton cpu offers upto 40% price-performance gains
                  compared to comparable previous generation x86 based EC2
                  instances depending upon nature of workload being run on
                  them</label
                >
              </div>
            </div>
          </div>
        </div>
        <br />
        <br />

        <div class="col-md-12">
          <div class="col-md-12">
            <input
              type="checkbox"
              v-model="isMaximizeCpuUtilCriteria"
              id="accept2"
              class="form-check-input"
            />

            <label class="form-check-label h3prompt" for="accept2"
              >Improve average CPU utilization of fleet above current level of
              {{ fleetAvgCpuUtil }} %</label
            >
          </div>
          <div>
            <div class="row">
              <div :disabled="isMaximizeCpuUtilCriteria != 1" class="col-md-4">
                <label :disabled="isMaximizeCpuUtilCriteria != 1"
                  >Target CPU Utilization % of fleet</label
                >
                <input
                  id="cpuUtil"
                  size="120"
                  autocomplete="on"
                  v-model="maxCpuUtilCriteria"
                  type="number"
                  class="form-control"
                  required
                  margin="2px"
                  :disabled="isMaximizeCpuUtilCriteria != 1"
                />
              </div>
              <div class="col-md-8">
                <label
                  :disabled="isMaximizeCpuUtilCriteria != 1"
                  class="text-muted helptext"
                  >Typical value for CPU utilization is around 80 %. However,
                  please choose a value that fits your specific workload's CPU
                  requirement after ensuring there's headroom for transient
                  spikes in CPU usage.</label
                >
              </div>
            </div>
          </div>
        </div>
        <br />
        <br />
        <div class="col-md-12">
          <div :disabled="fleetHasMemUtilMetric != 1" class="col-md-12">
            <input
              :disabled="fleetHasMemUtilMetric != 1"
              type="checkbox"
              v-model="isMaximizeMemUtilCriteria"
              id="accept3"
              class="form-check-input"
            />
            <label
              v-if="fleetHasMemUtilMetric == 1"
              class="form-check-label h3prompt"
              for="accept3"
              >Increase average Memory utilization of fleet above curret level
              of {{ fleetAvgMemUtil }}</label
            >
            <label v-else class="form-check-label h3prompt" for="accept3"
              >Increase average Memory utilization of fleet above curret
              level</label
            >
          </div>
          <div>
            <div class="row">
              <div :disabled="isMaximizeMemUtilCriteria != 1" class="col-md-4">
                <label :disabled="isMaximizeMemUtilCriteria != 1"
                  >Target Memory Utilization % of fleet</label
                >
                <input
                  id="cpuUtil"
                  size="120"
                  autocomplete="on"
                  v-model="maxMemUtilCriteria"
                  type="number"
                  class="form-control"
                  required
                  margin="2px"
                  :disabled="isMaximizeMemUtilCriteria != 1"
                />
              </div>
              <div class="col-md-8">
                <label
                  :disabled="isMaximizeMemUtilCriteria != 1"
                  class="text-muted helptext"
                  >Typical value for Memory utilization is around 70 %. However,
                  please choose a value that fits your specific workload's RAM
                  requirement after ensuring there's headroom for transient
                  spikes in RAM usage.</label
                >
              </div>
            </div>
          </div>
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
      </v-container>
    </div>
  </div>
</template>
<script>
import AmplifyStore from '../store/store';

export default {
  name: 'OptimizeCriteria',
  data() {
    return {
      fleetHasMemUtilMetric: false,
      maxCpuUtilCriteria: 80,
      maxMemUtilCriteria: 70,
      perfGainedGrav2Criteria: 0,
      hasGravitonPerfGainCriteria: false,
      isMaximizeCpuUtilCriteria: false,
      isMaximizeMemUtilCriteria: false,
      isDisableSubmit: false,
      targetCpuUtilHelpText: '',
      fleetAvgCpuUtil: null,
      fleetAvgMemUtil: null,
    };
  },
  created() {
    console.log('In created');

    this.fleetAvgCpuUtil = AmplifyStore.state.overProvFleet.fleetAvgCpuUtil;
    this.fleetHasMemUtilMetric =
      AmplifyStore.state.overProvFleet.hasAvgFleetMemUtil;

    this.fleetAvgMemUtil = AmplifyStore.state.overProvFleet.fleetAvgMemUtil;
  },
  methods: {
    processSubmit() {
      var optimizeCriteria = {};
      optimizeCriteria.maxCpuUtilCriteria = this.maxCpuUtilCriteria;
      optimizeCriteria.maxMemUtilCriteria = this.maxMemUtilCriteria;
      optimizeCriteria.perfGainedGrav2Criteria = this.perfGainedGrav2Criteria;
      optimizeCriteria.hasGravitonPerfGainCriteria =
        this.hasGravitonPerfGainCriteria;
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
      // not yet implemented
      return !this.isDisableSubmit;
    },
  },
};
</script>

