<script lang="ts">
  import ChatPlus from 'svelte-material-icons/ChatPlus.svelte';
  import {
    user,
    chatStore,
    roomStore,
    activeChats as allChats
  } from '../lib/store';
  import FormInput from './FormInput.svelte';
  import ChatList from './ChatList.svelte';
  import { toggleRoomWidget, showDetails, logout } from '../lib/utils';
  import { fetchUserChats, fetchCurrentChatOrRoom } from '../lib/messaging';
  import Button from './Button.svelte';
  import NewRoom from './NewRoom.svelte';
  import socket from '../lib/socket';
  import SearchResult from './SearchResult.svelte';
  import ChatView from './ChatView.svelte';

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
          chatName = (<Room>chat).name.toLowerCase();
        }
        if (chatName.includes(term)) return chat;
      });
      // update with result and return
      activeChats = matchedActiveChats;
      return;
    }
    // search through all users
    term = term.replace('@', '');
    socket.emit(
      'search_users',
      { search_term: term, id: $user.id },
      (payload) => {
        matches = payload.data;
      }
    );
  }

  $: activeChats = $allChats;
</script>

<section
  class="main-section relative flex items-center justify-center h-full w-full overflow-hidden"
>
  <div
    class="toast-container absolute inset-0 w-full md:max-w-[1040px] h-[100px] rounded-md text-sm italic"
  />
  <div
    class="block md:grid md:grid-cols-home w-full md:max-w-[1040px] h-full md:h-[550px] md:m-auto bg-dark-pri shadow-xl shadow-black overflow-hidden"
  >
    <aside
      class="left relative md:flex flex-col md:border-r md:border-r-gray-500 h-screen md:h-full w-full md:m-0 md:w-[350px] overflow-hidden transition-all duration-500"
    >
      <div
        class="header h-[75px] flex justify-between items-center py-4 px-6 space-x-5 border-b border-b-gray-500"
      >
        <button
          on:click={showDetails}
          data-username={$user.username}
          class="flex items-center py-4 px-6 space-x-5"
        >
          <div class="avatar relative w-10 h-10 rounded-full bg-pri-900">
            <i
              class="online block w-2 h-2 rounded-full bg-green-500 absolute top-0 right-1"
            />
          </div>
          <div class="username">@{$user.username}</div>
        </button>
        <div on:click={logout} on:keypress={logout}>
          <Button
            text="LOGOUT"
            dim={[3, 2]}
            type="button"
            styles="bg-sec-700 font-semibold text-xs"
          />
        </div>
      </div>
      <div
        class="flex flex-col justify-start items-center space-y-5 py-6 overflow-hidden"
      >
        <FormInput
          onKeyUp={search}
          placeholder="Search or start a new chat"
          type="text"
          name="search-input"
          styles="rounded-3xl bg-dark-sec w-4/5 md:w-min"
        />
        {#if matches.length > 0}
          <div
            class="absolute top-[125px] right-0 w-full px-8 z-50 h-full bg-dark-transp backdrop-blur-sm shadow-md"
          >
            <SearchResult bind:matches />
          </div>
        {/if}
        <h4 class="font-semibold text-lg self-start px-4">Messages</h4>
        <ChatList bind:activeChats />
        <NewRoom />
      </div>
      <button
        on:click={toggleRoomWidget}
        class="peer absolute right-4 bottom-4 w-12 h-12 rounded-full bg-pri-900 flex justify-center items-center shadow-lg shadow-black hover:shadow-none transition-shadow duration-300 z-50"
      >
        <ChatPlus size="2em" />
      </button>
    </aside>
    <div
      class="right absolute top-0 left-0 md:block md:relative w-full h-full md:h-[550px] overflow-hidden translate-x-full md:translate-x-0 transition-all duration-500"
    >
      <div class="md:block relative h-full md:h-[550px] overflow-hidden">
        {#if $chatStore || $roomStore}
          <ChatView />
        {:else}
          <div class="w-full h-[525px] flex justify-center items-center">
            <p class="">Welcome! Choose a chat on the left to get started</p>
          </div>
        {/if}
      </div>
    </div>
  </div>
</section>

<style>
  aside > div:nth-child(2) {
    height: calc(100vh - 75px);
  }
</style>
