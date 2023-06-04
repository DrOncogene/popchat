<script lang="ts">
  import Close from 'svelte-material-icons/Close.svelte';
  import MessageIcon from 'svelte-material-icons/MessageText.svelte'
  import { showDetails, newChat, closeDetails } from '../lib/helpers';
  import { chatStore, roomStore, user } from "../lib/store";
  import ProfileImage from "./ProfileImage.svelte";

  // if details is null, then we are in a chat/room view
  // else we are in a details view
  export let details = null;
</script>

<div id="" class="relative header h-[75px] w-full border-b border-b-gray-500 flex items-center flex-nowrap py-4 px-6">
{#if !details}
<!-- for chat/room views -->
  {#if $roomStore}
  <div data-id="{ $roomStore.id }" class="w-full flex flex-nowrap items-center">
    <ProfileImage />
    <a on:click={e => showDetails(e, 'room')} href="/" class="block ml-3">
      <p class="text-lg font-bold">{$roomStore.name}</p>
      <p class="text-sm font-thin italic text-left">{$roomStore.members.length}  members</p>
    </a>
  </div>
  {:else if $chatStore}
  {@const members = [$chatStore.user_1, $chatStore.user_2]}
  {@const user2 = members[0] === $user.username ? members[1] : members[0]}
  <div data-id="{ $chatStore.id }" class="w-full flex flex-nowrap items-center">
    <ProfileImage />
    <a on:click={e => showDetails(e, 'chat')} href="/" class="block ml-3">@{user2}</a>
  </div>
  {/if}
{:else if 'type' in details && details.type === 'room'}
  <div class="w-full flex flex-nowrap items-center" data-id={ details.id }>
    <ProfileImage />
    <p class="text-lg font-bold ml-2">{details.name}</p>
  </div>
  <a on:click={closeDetails} href="/" class="absolute right-0 mx-10"><Close size="1.5em" /></a>
{:else if 'type' in details && details.type === 'chat'}
{@const user2 = details.user_1 === $user.username ? details.user_2 : details.user_1}
  <div class="w-full flex flex-nowrap items-center">
    <ProfileImage />
    <p class="text-lg font-bold ml-2">@{ user2 }</p>
  </div>
  <a on:click={closeDetails} href="/" class="absolute right-0 mx-10"><Close size="1.5em" /></a>
{:else}
  <div data-username="{details.username}" class="w-full flex flex-nowrap items-center">
    <ProfileImage />
    <p class="text-lg font-bold ml-2">@{details.username}</p>
    <a on:click={newChat} href="/" class="ml-10">
      <MessageIcon size="1.5em" color="#1FDBA5" />
    </a>
  </div>
  <a on:click={closeDetails} href="/" class="absolute right-0 mx-10"><Close size="1.5em" /></a>
{/if}
</div>