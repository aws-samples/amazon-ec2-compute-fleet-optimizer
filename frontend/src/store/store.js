/*! Copyright Amazon.com Inc. or its affiliates.

SPDX-License-Identifier: MIT No Attribution(MIT-0)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. */

import Vue from 'vue';
import Vuex from 'vuex';
import apigClientFactory from 'aws-api-gateway-client';
import { Auth } from 'aws-amplify';
import config from '../aws-exports';

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    sessionCtx: null,
    computeOptReport: null,
    overProvFleet: null,
    overProvEc2: null,
    optimizeCrit: null,
  },
  mutations: {
    setUser(state, user) {
      if (user != null) {
        state.sessionCtx = {};

        state.sessionCtx.user = user;

        Auth.currentCredentials()
          .then((res) => {
            console.log('currentUserCred: ' + JSON.stringify(res, null, 2));
            state.sessionCtx.creds = res;

            var apigClient = apigClientFactory.newClient({
              invokeUrl: config.aws_cloud_logic_custom[0].endpoint, // REQUIRED

              region: config.aws_cloud_logic_custom[0].region, // REQUIRED: The region where the API is deployed.

              accessKey: state.sessionCtx.creds.accessKeyId, // REQUIRED

              secretKey: state.sessionCtx.creds.secretAccessKey, // REQUIRED

              sessionToken: state.sessionCtx.creds.sessionToken, // OPTIONAL: If you are using temporary credentials
              //you must include the session token.

              systemClockOffset: 0, // OPTIONAL: An offset value in milliseconds to apply to signing time

              retries: 4, // OPTIONAL: Number of times to retry before failing. Uses axios-retry plugin.

              retryCondition: (err) => {
                // OPTIONAL: Callback to further control if request should be retried.
                return err.response && err.response.status === 500; //           Uses axios-retry plugin.
              },

              shouldResetTimeout: false, // OPTIONAL: Defines if the timeout should be reset between retries. Unless
              //           `shouldResetTimeout` is set to `true`, the request timeout is
              //           interpreted as a global value, so it is not used for each retry,
              //           but for the whole request lifecycle.
            });
            state.sessionCtx.apigClient = apigClient;
          })
          .catch((err) => {
            console.log(err);
            console.log(
              'currentUserCred error : ' + JSON.stringify(err, null, 2)
            );
          });
      } else {
        state.sessionCtx = null;
      }
    },
    setComputeOptReport(state, loc) {
      if (loc != null) {
        state.computeOptReport = {};

        state.computeOptReport.s3Bucket = loc.s3Bucket;
        state.computeOptReport.s3ObjKey = loc.s3ObjKey;
      }
    },
    setOverProvEc2(state, seln) {
      if (seln != null) {
        state.overProvEc2 = {};

        state.overProvEc2.instanceArn = seln.selectedInstanceArn;
        state.overProvEc2.instanceType = seln.selectedInstanceType;
        state.overProvEc2.instanceName = seln.selectedInstanceName;
        state.overProvEc2.instanceTotalFleetInstCnt =
          seln.selectedInstanceTotalFleetInstCnt;
        state.overProvEc2.fleetId = seln.fleetId;
      }
    },
    setOverProvFleet(state, fleetData) {
      if (fleetData != null) {
        state.overProvFleet = {};

        state.overProvFleet.fleetId = fleetData.fleetId;
        state.overProvFleet.instances = fleetData.fleetInstances;
      }
    },
    setOptimizeCriteria(state, criteria) {
      if (criteria != null) {
        state.optimizeCrit = {};

        state.optimizeCrit.maxCpuUtilCriteria = criteria.maxCpuUtilCriteria;
        state.optimizeCrit.maxMemUtilCriteria = criteria.maxMemUtilCriteria;
        state.optimizeCrit.perfGainedGrav2Criteria =
          criteria.perfGainedGrav2Criteria;
        state.optimizeCrit.isMaximizeCpuUtilCriteria =
          criteria.isMaximizeCpuUtilCriteria;
        state.optimizeCrit.isMaximizeMemUtilCriteria =
          criteria.isMaximizeMemUtilCriteria;
      }
    },
  },
});

export default store;
