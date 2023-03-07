<script lang="ts">
  import { showDetails } from "../lib/helpers";

  export let type = 'chat';
  export let isDetail = false;
  export let username = "";
</script>

{#if !isDetail}
<div class="avatar block relative w-10 h-10 rounded-full bg-pri-900">
  <!-- <i class="online block w-2 h-2 rounded-full bg-green-500 absolute top-0 right-1"></i> -->
</div>
{:else}
<a
  on:click|stopPropagation={(e) => {showDetails(e, type)}}
  href="/"
  data-username={username}
  class="avatar block relative w-10 h-10 rounded-full bg-pri-900"
>
  <!-- <i class="online block w-2 h-2 rounded-full bg-green-500 absolute top-0 right-1"></i> -->
</a>
{/if}