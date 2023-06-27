<script lang="ts">
  import ChatPlus from 'svelte-material-icons/ChatPlus.svelte';
  import {
    user,
    chatStore,
    roomStore,
    activeChats as allChats,
  } from '../lib/store';
  import FormInput from './FormInput.svelte';
  import ChatList from './ChatList.svelte';
  import {
    fetchCurrentChatOrRoom,
    fetchUserChats,
    toggleRoomWidget,
    showDetails,
    logout
  } from '../lib/helpers';
  import Button from './Button.svelte';
  import NewRoom from './NewRoom.svelte';
  import socket from '../lib/socket';
  import SearchResult from './SearchResult.svelte';
  import ChatView from './ChatView.svelte';
  import DetailsView from './DetailsView.svelte';

  fetchUserChats();
  fetchCurrentChatOrRoom();
  
  let matches = [];

  function search(e: KeyboardEvent) {
    const input = <HTMLInputElement>e.target;
    let term: string = input.value.toLowerCase().trim();

    matches = [];
    if (term.replace('@', '').length === 0) {
      activeChats = $allChats;
      return;
    }
    // filter by type and search term
    if (!term.startsWith('@')) {
      const matchedActiveChats = $allChats.filter((chat) => {
        let chatName;
        if (chat.type === 'chat') {
          // @ts-ignore
          chatName = chat.user_1 === $user.username ? chat.user_2 : chat.user_1;
        } else {
          // @ts-ignore
          chatName = chat.name.toLowerCase();
        }
        if (chatName.includes(term)) return chat;
      });
      // update with result and return
      activeChats = matchedActiveChats;
      return;
    }
    // search through all users
    term = term.replace('@', '');
    socket.emit('get_users', { search_term: term, id: $user.id }, (payload) => {
      matches = payload.matches;
    });
  }

  $: activeChats = $allChats;
</script>

<section class="main-section grid md:grid-cols-home md:max-w-[1040px] h-[550px] m-auto bg-dark-pri shadow-xl shadow-black">
  <aside class="right hidden relative md:flex flex-col border-r border-r-gray-500 w-[350px] overflow-hidden">
    <div class="header h-[75px] flex justify-between items-center py-4 px-6 space-x-5 border-b border-b-gray-500">
      <button on:click={showDetails} data-username={$user.username} class="flex items-center py-4 px-6 space-x-5">
        <div class="avatar relative w-10 h-10 rounded-full bg-pri-900"><i class="online block w-2 h-2 rounded-full bg-green-500 absolute top-0 right-1"></i></div>
        <div class="username">@{$user.username}</div>
      </button>
      <div on:click={logout} on:keypress={logout}>
        <Button
          text='LOGOUT'
          dim={[3, 2]}
          type='button'
          styles='bg-sec-700 font-semibold text-xs'
        />
      </div>
    </div>
    <div class="flex flex-col justify-start items-center space-y-5 py-6 overflow-hidden">
      <FormInput
        onKeyUp={ search }
        placeholder='Search or start a new chat'
        type='text'
        name='search-input'
        styles='rounded-3xl bg-dark-sec'
      />
      {#if matches.length > 0}
      <div class="absolute top-[125px] right-0 w-full px-8 z-50 h-full bg-dark-transp backdrop-blur-sm shadow-md">
        <SearchResult bind:matches={ matches } />
      </div>
      {/if}
      <h4 class="font-semibold text-lg self-start px-4">Messages</h4>
      <ChatList bind:activeChats={ activeChats } />
      <NewRoom />
    </div>
    <button on:click={toggleRoomWidget} class="peer absolute right-2 bottom-2 w-12 h-12 rounded-full bg-pri-900 flex justify-center items-center shadow-lg shadow-black hover:shadow-none transition-shadow duration-300 z-50">
      <ChatPlus size="2em" />
    </button>
  </aside>

  <div class="relative left h-[550px] overflow-hidden">
    {#if $chatStore || $roomStore}
      <ChatView />
    {:else}
      <div class="w-full h-[525px] flex justify-center items-center">
        <p class="">Welcome! Choose a chat on the left to get started</p>
      </div>
    {/if}
  </div>
</section>

<style>

</style>