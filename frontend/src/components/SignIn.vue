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
  <div>
    <h2>Sign In</h2>
    <div class="formcontainer">
      <div class="form-group">
        <label class="font-weight-bold">User Id</label>
        <input
          placeholder="xxx@yyy.com"
          v-model="form.username"
          size="140"
          autocomplete="on"
          type="text"
          class="form-control"
          required
        />
      </div>
      <div class="form-group">
        <label class="font-weight-bold">Password</label>
        <input
          v-model="form.password"
          size="140"
          type="password"
          class="form-control"
          required
        />
      </div>
      <div align="right">
        <button v-on:click="signIn" class="btn btn-primary mt-3">
          Sign In
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { Auth } from 'aws-amplify';
//import * as AWS from 'aws-sdk';

export default {
  name: 'home',
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
    };
  },
  methods: {
    async signIn() {
      const { username, password } = this.form;
      try {
        const response = await Auth.signIn(username, password);
        console.log('User sign-in succeeded', response);
      } catch (err) {
        console.log('User sign-in falied... ', err);
        alert('Login failed - ' + err.message);
      }
      Auth.currentCredentials()
        .then((creds) => {
          console.log('currentUserCred: ' + JSON.stringify(creds, null, 2));
        })
        .catch((err) => {
          console.log(
            'currentUserCred error : ' + JSON.stringify(err, null, 2)
          );
        });

      // if Auth doesn't end up fetching AWS credentials for the above authenticated user,
      // let's use Cognito API to fetch those credentials

      //await this.getAWSTemporaryCreds(user);
      //const someCreds = AWS.config.credentials;
      //console.log(someCreds);
    },
  },
};
</script>
