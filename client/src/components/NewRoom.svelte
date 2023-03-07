<script lang="ts">
  import FormInput from './FormInput.svelte';
  import Close from 'svelte-material-icons/Close.svelte';
  import Button from './Button.svelte';
  import { displayFormError, toggleWidget } from '../lib/helpers';
  import { user, state, currentRoom } from '../lib/store';
  import socket from '../lib/socket';

  function createRoom(e: SubmitEvent) {
    e.preventDefault();

    const nameInput: HTMLInputElement = document.querySelector('#room-name');
    const memberInput: HTMLInputElement = document.querySelector('#new-member');

    const payload = {
      member: memberInput.value.trim(),
      room_data: {
        name: nameInput.value.trim(),
        created_by: $user.id
      }
    };

    socket.emit('create_room', payload, (payload) => {
      if (payload.status !== 201) {
        displayFormError('User does not exist', memberInput);
        return;
      }
      socket.emit('get_user', $user.id, (payload: User) => {
        user.set(payload);
      });
      const newRoom: Chat = payload.room;
      for (let chat of $user.all_chats) {
        if (chat.id !== newRoom.id) continue;
        $state.room = chat;
        break;
      }
      $currentRoom = newRoom;
    });
    toggleWidget(e);
  }
</script>

<div class="hidden absolute right-8 bottom-8 min-h-[200px] p-4 bg-pri-900 shadow-lg shadow-black transition-all duration-700" id="new-room-widget">
  <form on:submit={e => createRoom(e)} class="relative flex flex-col justify-center items-center">
    <a on:click={e => toggleWidget(e)} href="/" class="absolute -right-2 -top-2"><Close /></a>
    <p class="invisible text-xs text-center w-full text-red-500" id="form-errors">An error</p>
    <FormInput
      name='room-name'
      placeholder='Enter room name'
      styles='mt-6'
    />
    <FormInput
      name='new-member'
      placeholder='Add one member'
      styles='mt-6'
    />
    <Button
      text='Create Room'
      type='submit'
      dim={[2, 2]}
      styles='text-xs mt-6 self-end font-thin'
    />
  </form>
</div>