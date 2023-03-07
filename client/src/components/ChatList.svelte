<script lang="ts">
  import { user, currentRoom, currentChat } from "../lib/store";
  import ProfileImage from './ProfileImage.svelte';
  import { openChat } from "../lib/helpers";

  export let activeChats: Chat[];
</script>

{#key $currentChat || $currentRoom}
<ul class="flex flex-col  w-full overflow-x-hidden overflow-y-auto" id="chat-list">
{#each activeChats as chat}
{@const current = $currentChat ? $currentChat : $currentRoom}
{@const selected = current && chat.id === current.id ? 'bg-sec-700' : ''}
{#if chat.type === 'room'}
  <li on:click={ openChat } on:keypress={ openChat } data-type="{chat.type}" data-id="{chat.id}" class="flex items-center space-x-2 py-2 px-6 mb-0.5 cursor-pointer hover:bg-sec-700 overflow-x-hidden transition-all duration-250 {selected}">
    <ProfileImage
      type={chat.type}
      isDetail={true}
    />
    <div class="flex flex-col overflow-hidden">
      <h6 class="text-base font-semibold overflow-hiddenmax-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">{chat.name}</h6>
      {#if chat.last_msg && chat.last_msg.sender === $user.username}
        <p class="text-xs italic font-thin max-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">You: {chat.last_msg.text}</p>
      {:else if chat.last_msg}
        <p class="text-xs italic font-thin max-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">{chat.last_msg.sender}: {chat.last_msg.text}</p>
      {/if}
    </div>
  </li>
  {:else}
  {@const user2 = chat.members[0] === $user.username ? chat.members[1] : chat.members[0]}
  <li on:click={(e) => openChat(e)} on:keypress={(e) => openChat(e)} data-type="{chat.type}" data-id="{chat.id}" class="flex items-center space-x-2 py-2 px-6 mb-0.5 cursor-pointer hover:bg-sec-700 overflow-x-hidden transition-all duration-250 {selected}">
    <ProfileImage
      type={chat.type}
      isDetail={true}
      username={user2}
    />
    <div class="flex flex-col overflow-hidden">
      <h6 class="text-base font-semibold overflow-hiddenmax-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">@{user2}</h6>
      {#if chat.last_msg}
        <p class="text-xs italic font-thin max-w-[250px] text-ellipsis whitespace-nowrap overflow-hidden">{chat.last_msg.text}</p>
      {/if}
    </div>
  </li>
  {/if}
{/each}
</ul>
{/key}

<style>

</style>