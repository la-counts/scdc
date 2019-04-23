import Vue from 'vue'
import SavedStatus from './SavedStatus.vue'
import SavedSearch from './SavedSearch.vue'

Vue.component('saved-status', SavedStatus);
Vue.component('saved-search', SavedSearch);

document.addEventListener('DOMContentLoaded', function() {
  function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = jQuery.trim(cookies[i]);
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
  window.csrftoken = getCookie('csrftoken');

  new Vue({
    el: "saved-status",
    component: SavedStatus
  });
  new Vue({
    el: "saved-search",
    component: SavedSearch
  });
});
