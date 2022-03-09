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
        Upload the exported CSV report from AWS Compute Optimizer containing
        recommendations
      </p>
    </div>
    <div class="row mt-2">
      <div class="form-group col-md-12">
        <!--UPLOAD-->
        <form
          enctype="multipart/form-data"
          novalidate
          v-if="isInitial || isSaving"
        >
          <div class="dropbox">
            <input
              type="file"
              multiple
              :name="uploadFieldName"
              :disabled="isSaving"
              @change="
                onFileChange($event.target.files);
                fileCount = $event.target.files.length;
              "
              accept="text/csv"
              class="input-file"
            />
            <p v-if="isInitial">
              Drag your file here to begin<br />
              or click to browse
            </p>
            <p v-if="isSaving">Uploading {{ fileCount }} files...</p>
          </div>
        </form>
        <div v-if="isSuccess">
          <h2>Uploaded {{ uploadedFiles.length }} file(s) successfully.</h2>
          <p>
            <a href="javascript:void(0)" @click="reset()">Upload again</a>
          </p>
        </div>
        <!--FAILED-->
        <div v-if="isFailed">
          <h2>Uploaded failed.</h2>
          <p>
            <a href="javascript:void(0)" @click="reset()">Try again</a>
          </p>
          <pre>{{ uploadError }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import AmplifyStore from '../store/store';

const STATUS_INITIAL = 0,
  STATUS_SAVING = 1,
  STATUS_SUCCESS = 2,
  STATUS_FAILED = 3;

export default {
  name: 'ec2coreportupload',
  data() {
    return {
      isDisableSubmit: false,
      uploadedFiles: [],
      uploadError: null,
      currentStatus: null,
      uploadFieldName: 'photos',
    };
  },
  computed: {
    isInitial() {
      return this.currentStatus === STATUS_INITIAL;
    },
    isSaving() {
      return this.currentStatus === STATUS_SAVING;
    },
    isSuccess() {
      return this.currentStatus === STATUS_SUCCESS;
    },
    isFailed() {
      return this.currentStatus === STATUS_FAILED;
    },
  },
  mounted() {
    this.reset();
  },
  methods: {
    reset() {
      // reset form to initial state
      this.currentStatus = STATUS_INITIAL;
      this.uploadedFiles = [];
      this.uploadError = null;
    },
    processSubmit() {
      var computeOptReport = {};
      computeOptReport.image = this.image;

      AmplifyStore.commit('setComputeOptReport', computeOptReport);

      this.$router.push({
        path: 'overprovfleets',
      });
    },
    isSubmitable: function () {
      return !this.isDisableSubmit;
    },
    onFileChange(files) {
      if (!files.length) return;
      this.currentStatus = STATUS_SUCCESS;
      this.createImage(files[0]);
    },
    createImage(file) {
      // var image = new Image()
      let reader = new FileReader();
      const MAX_IMAGE_SIZE = 5000000;
      reader.onload = (e) => {
        console.log('length: ', e.target.result.includes('data:text/csv'));
        if (!e.target.result.includes('data:text/csv')) {
          return alert('Wrong file type');
        }
        if (e.target.result.length > MAX_IMAGE_SIZE) {
          return alert('File too large');
        }
        this.image = e.target.result;
        this.processSubmit();
      };
      reader.readAsDataURL(file);
    },
  },
};
</script>

<style lang="scss">
.dropbox {
  outline: 2px dashed grey; /* the dash box */
  outline-offset: -10px;
  background: lightcyan;
  color: dimgray;
  padding: 10px 10px;
  min-height: 200px; /* minimum height */
  position: relative;
  cursor: pointer;
}

.input-file {
  opacity: 0; /* invisible but it's there! */
  width: 100%;
  height: 200px;
  position: absolute;
  cursor: pointer;
}

.dropbox:hover {
  background: lightblue; /* when mouse over to the drop zone, change color */
}

.dropbox p {
  font-size: 1.2em;
  text-align: center;
  padding: 50px 0;
}
</style>
