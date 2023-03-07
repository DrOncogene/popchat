<script lang="ts">
  import { currentDetail} from "../lib/store";
  import socket from "../lib/socket";
  import { showDetails } from "../lib/helpers";

  export let matches: User[];

  function showDetailsFromSearch(e: Event, type=null) {
    showDetails(e)
    matches = [];
  }
</script>

<ul id="search-dropdown" class="bg-pri-900 w-full h-max flex flex-col justify-center items-center rounded-lg">
  {#each matches as match}
    <li on:click={e => showDetailsFromSearch(e)} on:keydown={e => showDetailsFromSearch(e)} data-id={match.id} class="px-3 py-2 w-full">
      <a href="/" class="w-full block">{match.username}</a>
    </li>
  {/each}
</ul>