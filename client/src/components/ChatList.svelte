<script lang="ts">
  import { user, roomStore, chatStore } from "../lib/store";
  import ProfileImage from './ProfileImage.svelte';
  import { openChat } from "../lib/helpers";
  import { flip } from "svelte/animate";

  export let activeChats; // active chats
</script>

{#key $chatStore || $roomStore}
<ul class="flex flex-col flex-nowrap w-full h-min overflow-x-hidden overflow-y-auto" id="chat-list">
{#each [...activeChats].reverse() as chat (chat.id)}
{@const current = $chatStore ? $chatStore : $roomStore}
{@const selected = current && chat.id === current.id ? 'md:bg-sec-700' : ''}
<li animate:flip={{duration: 500}}  on:click={ (e) => openChat(e) } on:keypress={ (e) => openChat(e) } data-type="{chat.type}" data-id="{chat.id}" class="flex shrink-0 items-center space-x-2 h-[60px] py-2 px-6 mb-0.5 cursor-pointer hover:bg-sec-700 overflow-hidden transition-all duration-250 {selected}">
  <ProfileImage />
  <div class="flex flex-col overflow-hidden">
    {#if chat.type === 'room'}
      <h6 class="text-base font-semibold overflow-hiddenmax-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">{chat.name}</h6>
    {:else}
    {@const user2 = chat.user_1 === $user.username ? chat.user_2 : chat.user_1 }
      <h6 class="text-base font-semibold overflow-hiddenmax-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">@{user2}</h6>
    {/if}
    {#if chat.last_msg && chat.last_msg.sender === $user.username}
      <p class="text-xs italic font-thin max-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">You: {chat.last_msg.text}</p>
    {:else if chat.last_msg}
      <p class="text-xs italic font-thin max-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">{chat.last_msg.sender}: {chat.last_msg.text}</p>
    {/if}
  </div>
</li>
{:else}
<p class="text-base font-semibold text-center w-full">No chats</p>
{/each}
</ul>
{/key}

<style>

</style>