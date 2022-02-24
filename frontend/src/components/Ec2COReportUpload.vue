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
        Enter S3 object key of file with EC2 recommendations from AWS Compute
        Optimizer
      </p>
    </div>
    <div class="row mt-2">
      <form class="mt-2">
        <div class="form-group">
          <label class="font-weight-bold">S3 object key name</label>
          <div class="col-md-4">
            <input
              id="s3ObjectKey"
              size="140"
              autocomplete="on"
              v-model="s3ObjectKey"
              type="text"
              class="form-control"
              placeholder="Text input"
              required
            />
          </div>
        </div>
        <div id="form-response"></div>
        <button
          v-if="isSubmitable"
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
import config from '../aws-exports';
import AmplifyStore from '../store/store';

export default {
  name: 'ec2coreportupload',
  data() {
    return {
      s3BucketName: `${config.aws_user_files_s3_bucket}`,
      s3ObjectKey: '',
      isDisableSubmit: false,
    };
  },
  methods: {
    processSubmit() {
      var computeOptReport = {};
      computeOptReport.s3Bucket = this.s3BucketName;
      computeOptReport.s3ObjKey = this.s3ObjectKey;

      AmplifyStore.commit('setComputeOptReport', computeOptReport);

      this.$router.push({
        path: 'overprovfleets',
      });
    },
    isSubmitable: function () {
      return !this.isDisableSubmit;
    },
  },
};
</script>
