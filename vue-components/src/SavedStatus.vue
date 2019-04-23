<template>
  <a v-if="following" class="saved no-hover" v-bind:href="url" v-on:click="unfollow">
    <span class="save-star"><i class="fa fa-star" aria-hidden="true"></i></span>
    <span class="save-text">Remove from my account</span>
  </a>
  <a v-else class="unsaved no-hover" v-bind:href="url" v-on:click="follow">
    <span class="save-star"><i class="fa fa-star-o" aria-hidden="true"></i></span>
    <span class="save-text">Save to my account</span>
  </a>
</template>

<script>
module.exports = {
  props: ['href'],
  data: function() {
    var parts = this.href.split('/');
    return {
      following: parts[parts.length-4] == "unfollow",
    }
  },
  methods: {
    follow: function(event) {
      event.preventDefault();
      var self = this;
      axios.get(this.url).then(function(response) {
        self.following = true;
      })
    },
    unfollow: function(event) {
      event.preventDefault()
      var self = this;
      axios.get(this.url).then(function(response) {
        self.following = false;
      })
    }
  },
  computed: {
    url: function() {
      var parts = this.href.split('/')
      var adjective = this.following ? 'unfollow' : 'follow'
      parts[parts.length-4] = adjective
      return parts.join('/')
    }
  }
}
</script>
