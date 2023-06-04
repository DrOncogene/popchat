<script lang="ts">
  import Close from 'svelte-material-icons/Close.svelte';
  import MessageIcon from 'svelte-material-icons/MessageText.svelte'
  import { showDetails, newChat, closeDetails } from '../lib/helpers';
  import { state, currentChat, currentRoom, currentDetail, user } from "../lib/store";
  import ProfileImage from "./ProfileImage.svelte";

  export let details = null;
</script>

<div id="" class="relative header h-[75px] w-full border-b border-b-gray-500 flex items-center flex-nowrap py-4 px-6">
{#if !details}
  {#if $currentRoom}
  <div data-id="{$currentRoom.id}" class="w-full flex flex-nowrap items-center">
    <ProfileImage type='room' />
    <a on:click={e => showDetails(e, 'room')} href="/" class="block ml-3">
      <p class="text-lg font-bold">{$currentRoom.name}</p>
      <p class="text-sm font-thin italic text-left">{$currentRoom.members.length}  members</p>
    </a>
  </div>
  {:else if $currentChat}
  {@const members = [$currentChat.user_1, $currentChat.user_2]}
  {@const user2 = members[0] === $user.username ? members[1] : members[0]}
  <div data-id="{user2}" class="w-full flex flex-nowrap items-center">
    <ProfileImage isDetail={true} />
    <a on:click={e => showDetails(e, 'chat')} href="/" class="block ml-3">@{user2}</a>
  </div>
  {/if}
{:else if 'type' in details && details.type === 'room'}
<div class="w-full flex flex-nowrap items-center">
  <ProfileImage type='room' />
  <p class="text-lg font-bold ml-2">{details.name}</p>
</div>
<a on:click={closeDetails} href="/" class="absolute right-0 px-10"><Close size="1.5em" /></a>
{:else}
  <div data-username="{details.username}" class="w-full flex flex-nowrap items-center">
    <ProfileImage />
    <p class="text-lg font-bold ml-2">@{details.username}</p>
    <a on:click={newChat} href="/" class="ml-10">
      <MessageIcon size="1.5em" color="#1FDBA5" />
    </a>
  </div>
  <a on:click={closeDetails} href="/" class="absolute right-0 px-10"><Close size="1.5em" /></a>
{/if}
</div>