<script lang="ts">
  import { fly } from "svelte/transition";
  import MessageIcon from "svelte-material-icons/MessageText.svelte"
  import { currentDetail, user } from "../lib/store";
  import ChatHeader from "./ChatHeader.svelte";
  import { newChat } from "../lib/helpers";

</script>

{#key $currentDetail}
{#if $currentDetail}
<div id="details-popup" class="absolute top-0 left-0 h-full w-full px-5 z-[500] flex justify-center items-end bg-transparent backdrop-blur-sm">
  <div transition:fly={{duration:200, y:200 }} class="w-[500px] h-3/4 bg-dark-sec overflow-auto backdrop-blur-lg">
    <ChatHeader details={$currentDetail} />
    {#if 'type' in $currentDetail}
    <h4 class="font-bold text-xl px-5 pt-5">Members</h4>
    <ul class="p-5 flex flex-col space-y-3">
      {#each $currentDetail.members as member}
        <li data-username={member} class="flex flex-nowrap justify-between">
          {#if member !== $user.username}  
            @{member}
          {:else}
            You
          {/if}
          {#if $currentDetail.admins.includes(member)}
            <span class="text-xs py-1 px-2 bg-sec-900 rounded-xl">Admin</span>
          {/if}
          <a on:click={ newChat } href="/" class="">
            <MessageIcon size="1.5em" color="#1FDBA5" />
          </a>
        </li>
      {/each}
    </ul>
    {:else}
    <p class="p-5 flex flex-col">Email: {$currentDetail.email}</p>
    {/if}
  </div>
</div>
{/if}
{/key}
