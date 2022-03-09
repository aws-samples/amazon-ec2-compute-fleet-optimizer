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
import VueRouter from 'vue-router';
import { Auth } from 'aws-amplify';
import AmplifyStore from './store/store';

import AuthComponent from './components/Auth';
import Ec2COReportUpload from './components/Ec2COReportUpload';
import OverProvFleets from './components/OverProvFleets';
import OptimizeCriteria from './components/OptimizeCriteria';
import RecoList from './components/RecoList';

const routes = [
  { path: '/', component: Ec2COReportUpload, meta: { requiresAuth: true } },
  { path: '/auth', component: AuthComponent },
  {
    path: '/overprovfleets',
    component: OverProvFleets,
    meta: { requiresAuth: true },
  },
  {
    path: '/optimizecriteria',
    component: OptimizeCriteria,
    meta: { requiresAuth: true },
  },
  { path: '/recolist', component: RecoList, meta: { requiresAuth: true } },
];

Vue.use(VueRouter);
//Vue.use(AmplifyPlugin, AmplifyModules);

//let user;

/* let user;

getUser().then((user, error) => {
  if (user) {
    //router.push({path: '/profile'})
  } else {
    console.log(error)
  }
}) */

async function getUser() {
  return Auth.currentAuthenticatedUser()
    .then((data) => {
      if (data && data.signInUserSession) {
        console.log('In 11111');
        AmplifyStore.commit('setUser', data);
        return data;
      }
      console.log('333333');
    })
    .catch((err) => {
      console.log('In 2222222');

      AmplifyStore.commit('setUser', null);
      console.log(err);
      throw err;
    });
}

const router = new VueRouter({
  routes,
});

router.beforeResolve((to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    getUser()
      .then(() => {
        next();
      })
      .catch(() => {
        next({
          path: '/auth',
        });
      });
  }
  next();
});

export default router;
