<script lang="ts">
  import FormInput from './FormInput.svelte';
  import Close from 'svelte-material-icons/Close.svelte';
  import Button from './Button.svelte';
  import { changeState, fetchCurrentChatOrRoom, fetchUserChats, showFormError, toggleRoomWidget } from '../lib/helpers';
  import { user, state, roomStore, activeChats as chatsAndRooms } from '../lib/store';
  import socket from '../lib/socket';

  function createRoom(e: SubmitEvent) {
    e.preventDefault();

    const nameInput = <HTMLInputElement>document.querySelector('#room-name');
    const memberInput = <HTMLInputElement>document.querySelector('#new-members');

    if (!nameInput.value.trim() || !memberInput.value.trim()) {
      showFormError('Name and members are required');
      return;
    }

    let membersArray = memberInput.value.trim().split(';');
    membersArray = membersArray.filter((member) => {
      return member.trim() !== '';
    });
    membersArray = membersArray.map(member => member.trim());

    const payload = {
      creator: $user.id,
      members: membersArray,
      name: nameInput.value.trim(),
    };

    socket.emit('create_room', payload, (payload) => {
      if (payload.status !== 201) {
        showFormError('User does not exist', memberInput);
        return;
      }
      const newRoom: Room = payload.room;

      fetchUserChats();
      changeState('home', null, newRoom.id);
      roomStore.set(newRoom);
      fetchCurrentChatOrRoom();
      toggleRoomWidget(e);
    });
  }
</script>

<div class="hidden absolute right-8 bottom-8 min-h-[200px] p-4 bg-pri-900 shadow-lg shadow-black transition-all duration-700" id="new-room-widget">
  <form on:submit={e => createRoom(e)} class="relative flex flex-col justify-center">
    <button on:click={e => toggleRoomWidget(e)} class="absolute -right-2 -top-2"><Close /></button>
    <p class="invisible text-xs text-center w-full text-red-500" id="form-errors">An error</p>
    <FormInput
      name='room-name'
      placeholder='Enter room name'
      styles='mt-6'
      errorMsg={ [true, 'room name required'] }
    />
    <FormInput
      name='new-members'
      placeholder='Add members'
      styles='mt-3'
      errorMsg={ [true, 'usernames separated by semicolons'] }
    />
    <Button
      text='Create Room'
      type='submit'
      dim={[2, 2]}
      styles='text-xs mt-6 self-end font-thin'
    />
  </form>
</div>