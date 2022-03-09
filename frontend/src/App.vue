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
  <div id="app">
    <div class="page-container">
      <div class="content-wrap">
        <div class="sign-out">
          <b-button
            id="btn1"
            v-b-tooltip.delay="{ show: '10', hide: '50' }"
            :title="emailId"
            variant="outline-success"
            v-if="signedIn"
            v-on:click="signOut"
            class="btn btn-primary mt-3 float-right"
          >
            Sign Out
          </b-button>
        </div>
        <router-view></router-view>
      </div>
      <footerComponent class="footerComp" />
    </div>
  </div>
</template>

<script>
import { Auth, Hub } from 'aws-amplify';
import footerComponent from '@/components/Footer.vue';

export default {
  name: 'app',
  components: {
    footerComponent,
  },
  data() {
    return {
      signedIn: false,
      emailId: '',
    };
  },
  beforeCreate() {
    Hub.listen('auth', (data) => {
      console.log('data:', data);
      const { payload } = data;
      if (payload.event === 'signIn') {
        this.signedIn = true;
        this.emailId = payload.data.attributes.email;
        this.$router.push('/');
      }
      if (payload.event === 'signOut') {
        this.$router.push('/auth');
        this.emailId = '';
        this.signedIn = false;
      }
    });
    Auth.currentAuthenticatedUser()
      .then(() => {
        this.signedIn = true;
      })
      .catch(() => (this.signedIn = false));
  },
  methods: {
    async signOut() {
      try {
        await Auth.signOut();
      } catch (error) {
        console.log('error signing out: ', error);
      }
    },
  },
};
</script>

<style>
.page-container {
  position: relative;
  min-height: 100vh;
}
.content-wrap {
  padding-bottom: 2.5rem; /* Footer height */
}
.footerComp {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 2.5rem;
}
.nav {
  display: flex;
}
.nav p {
  padding: 0px 30px 0px 0px;
  font-size: 18px;
  color: #000;
}
.nav p:hover {
  opacity: 0.7;
}
.nav p a {
  text-decoration: none;
}
.sign-out {
  margin: 0 auto;
  padding: 20px;
}
.button {
  float: right;
}
.v-data-table > .v-data-table__wrapper > table > tbody > tr > th,
.v-data-table > .v-data-table__wrapper > table > thead > tr > th,
.v-data-table > .v-data-table__wrapper > table > tfoot > tr > th {
  font-size: 14px !important;
}

.loader {
  border: 16px solid #f3f3f3;
  border-top: 16px solid #3498db;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.highlight {
  background-color: LightSkyBlue;
}

.cellhighlight {
  color: Green;
}

tr:hover {
  cursor: pointer;
}

.h1title {
  font-weight: bold;
  font-size: 30px;
}
.h2prompt {
  font-weight: bold;
  font-size: 20px;
}
.h3prompt {
  font-weight: bold;
  font-size: 16px;
}
.form-wrapper {
  width: 30vw;
  height: 60vh;
  background-image: url(/images/background.png);
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center bottom;
  font-family: 'fairplex-wide';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.helptext {
  font-size: small;
}
.input[type='checkbox'].checkbox_1 {
  display: none;
}
</style>
