/*!
Copyright Amazon.com Inc. or its affiliates.

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
import VueRouter from 'vue-router';
import Amplify from 'aws-amplify';
import '@aws-amplify/ui-vue';
import config from './aws-exports';
import store from './store/store';
import BootstrapVue from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import App from './App';
import router from './router';

import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';

/*****/
//import '@mdi/font/css/materialdesignicons.css'
//import 'vuetify/lib/styles/main.sass'
// import { createVuetify } from 'vuetify'
// import * as components from 'vuetify/lib/components'
// import * as directives from 'vuetify/lib/directives'

// const vuetify= createVuetify({
//    components,
//    directives,
//  })
/****/

Amplify.configure(config);

Vue.use(Vuetify, VueRouter, BootstrapVue, Vuetify);
Vue.config.productionTip = false;

Vue.prototype.$apiPath = '/price-performance-optimize';

// new Vue({
//   router,
//   store,
//   render: h => h(App)
// }).$mount('#app')

new Vue({
  router,
  store,
  vuetify: new Vuetify(),
  render: (h) => h(App),
}).$mount('#app');
