<script lang="ts">
  import { } from "../lib/store";
  import socket from "../lib/socket";
  import { showDetails } from "../lib/helpers";

  export let matches: User[];

  function showDetailsFromSearch(e: Event) {
    showDetails(e)
    matches = [];
  }
</script>

{#if matches.length > 0}
<ul id="search-dropdown" class="bg-pri-900 w-full h-max flex flex-col justify-center items-center shadow-2xl rounded-md">
  {#each matches as match}
    <li data-id={match.id} class="w-full px-5 py-3 hover:bg-sec-700">
      <a on:click={e => showDetailsFromSearch(e)} href="/" class="w-full block">{match.username}</a>
    </li>
  {/each}
</ul>
{/if}