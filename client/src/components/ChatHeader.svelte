<script lang="ts">
  import Close from 'svelte-material-icons/Close.svelte';
  import MessageIcon from 'svelte-material-icons/MessageText.svelte';
  import PencilIcon from 'svelte-material-icons/Pencil.svelte';
  import ChevronLeft from 'svelte-material-icons/ChevronLeft.svelte';
  import {
    showDetails,
    closeDetails,
    formatDate,
    switchView
  } from '../lib/utils';
  import { newChat, editRoomName, leaveRoom } from '../lib/messaging';
  import { chatStore, roomStore, user } from '../lib/store';
  import ProfileImage from './ProfileImage.svelte';
  import FormInput from './FormInput.svelte';
  import Button from './Button.svelte';

  // if details is null, then we are in a chat/room view
  // else we are in a details view
  export let details = null;

  function displayEditForm(e: Event) {
    e.preventDefault();

    document.getElementById('room-name-div').classList.toggle('hidden');
    document.getElementById('edit-room-form').classList.toggle('hidden');
    document.getElementById('edit-room-form').classList.toggle('flex');
    document.getElementById('edit-btn').classList.toggle('hidden');
    document
      .querySelector('#details-popup .header .avatar')
      ?.classList.toggle('hidden');
  }
</script>

<div
  id=""
  class="relative header h-[75px] w-full border-b border-b-gray-500 flex items-center flex-nowrap p-3 md:py-4 md:px-6"
>
  {#if !details}
    <!-- for chat/room views -->
    {#if $roomStore}
      <div data-id={$roomStore.id} class="w-full flex flex-nowrap items-center">
        <button
          on:click={(e) => switchView(e, 'close')}
          class="md:hidden -ml-4"
        >
          <ChevronLeft size="4em" />
        </button>
        <ProfileImage />
        <button
          title="Click to show details"
          on:click={(e) => showDetails(e, 'room')}
          class="block ml-3"
        >
          <p class="text-base md:text-lg font-bold">{$roomStore.name}</p>
          <p class="text-sm font-thin italic text-left">
            {$roomStore.members.length} members
          </p>
        </button>
        <Button
          dim={[2, 1]}
          text="Leave"
          title="Leave room"
          styles="md:font-bold text-xs md:px-4 md:py-2 ml-auto"
          onClick={(e) => leaveRoom(e)}
        />
      </div>
    {:else if $chatStore}
      {@const members = [$chatStore.user_1, $chatStore.user_2]}
      {@const user2 = members[0] === $user.username ? members[1] : members[0]}
      <div data-id={$chatStore.id} class="w-full flex flex-nowrap items-center">
        <button on:click={switchView} class="md:hidden mr-2">
          <ChevronLeft size="4em" />
        </button>
        <ProfileImage />
        <a on:click={(e) => showDetails(e, 'chat')} href="/" class="block ml-3"
          >@{user2}</a
        >
      </div>
    {/if}
  {:else if 'type' in details && details.type === 'room'}
    {@const creator =
      details.creator === $user.username ? 'You' : `@${details.creator}`}
    <div class="w-full flex flex-nowrap items-center" data-id={details.id}>
      <ProfileImage />
      <div class="flex flex-col justify-center ml-3" id="room-name-div">
        <p class="text-lg font-bold">{details.name}</p>
        <p class="text-xs italic">
          Created {formatDate(details.created_at)} by {creator}
        </p>
      </div>
      <form
        class="justify-between items-center ml-3 space-x-3 hidden"
        id="edit-room-form"
      >
        <FormInput
          type="text"
          name="room-name-change"
          value={details.name}
          styles="rounded-3xl"
        />
        <Button
          dim={[2, 1]}
          type="submit"
          text="Save"
          styles="md:font-bold text-xs md:px-4 md:py-2"
          onClick={editRoomName}
        />
        <Button
          dim={[2, 1]}
          text="Cancel"
          styles="md:font-bold text-xs md:px-4 md:py-2"
          onClick={displayEditForm}
        />
      </form>
    </div>
    {#if details.admins.includes($user.username)}
      <button
        on:click={displayEditForm}
        title="Edit name"
        class="absolute right-20"
        id="edit-btn"
      >
        <PencilIcon size="1.5em" />
      </button>
    {/if}
    <button on:click={closeDetails} title="close" class="absolute right-0 mx-5">
      <Close size="1.5em" />
    </button>
  {:else if 'type' in details && details.type === 'chat'}
    {@const user2 =
      details.user_1 === $user.username ? details.user_2 : details.user_1}
    <div class="w-full flex flex-nowrap items-center">
      <ProfileImage />
      <div class="flex flex-col justify-center ml-3">
        <p class="text-lg font-bold">@{user2}</p>
        <p class="text-xs italic">
          Started on: {formatDate(details.created_at)}
        </p>
      </div>
    </div>
    <button
      on:click={closeDetails}
      title="close"
      class="absolute right-0 mx-10"
    >
      <Close size="1.5em" />
    </button>
  {:else}
    <div
      data-username={details.username}
      class="w-full flex flex-nowrap items-center"
    >
      <ProfileImage />
      <p class="text-lg font-bold ml-2">@{details.username}</p>
      {#if details.username !== $user.username}
        <button
          title="Send message"
          data-username={details.username}
          on:click={newChat}
          class="ml-10"
        >
          <MessageIcon size="1.5em" color="#1FDBA5" />
        </button>
      {/if}
    </div>
    <button
      on:click={closeDetails}
      title="close"
      class="absolute right-0 mx-10"
    >
      <Close size="1.5em" />
    </button>
  {/if}
</div>
