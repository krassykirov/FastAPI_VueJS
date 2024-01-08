import { createApp } from 'vue'
import App from './App.vue'
import VueCookies from 'vue-cookies'
import $ from 'jquery'
window.$ = window.jQuery = $
import 'bootstrap'
import 'bootstrap-vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faStar, faPhone } from '@fortawesome/free-solid-svg-icons'

library.add(faStar, faPhone)

import router from './router'
import BootstrapVue3 from 'bootstrap-vue-3'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css'

const app = createApp(App)

app
  .use(router)
  .use(VueCookies)
  .use(BootstrapVue3)
  .component('font-awesome-icon', FontAwesomeIcon)
  .mount('#app')