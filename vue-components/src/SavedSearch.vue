<template>
  <a v-if="following" class="saved" v-bind:href="url" v-on:click="unfollow">
    <span class="save-star"><i class="fa fa-star" aria-hidden="true"></i></span>
    <span class="save-text">Saved to my account</span>
  </a>
  <a v-else class="unsaved" v-bind:href="url" v-on:click="follow">
    <span class="save-star"><i class="fa fa-star-o" aria-hidden="true"></i></span>
    <span class="save-text">Save to my account</span>
  </a>
</template>

<script>
module.exports = {
  props: ['href', 'searchdata'],
  data: function() {
    return {
      following: false,
    }
  },
  methods: {
    follow: function(event) {
      event.preventDefault();
      var self = this;
      axios.post(this.href, this.searchdata, {
          headers: {'X-CSRFToken': window.csrftoken},
        }).then(function(response) {
        self.following = true;
      })
    },
    unfollow: function(event) {
      event.preventDefault()
      var self = this;
      axios.delete(this.href, {
          headers: {'X-CSRFToken': window.csrftoken},
          data: this.searchdata,
        }).then(function(response) {
        self.following = false;
      })
    }
  }
}
</script>
