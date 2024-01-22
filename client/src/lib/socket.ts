import io from 'socket.io-client';
import { get } from 'svelte/store';
import { activeChats, chatStore, roomStore, user, state } from '../lib/store';
import {
  addMessageToChat,
  fetchUserChats,
  updateChatList,
  fetchCurrentChatOrRoom
} from './messaging';
import { changeState, getDetailsTarget } from './utils';
import notify from './notify';
import DetailsView from '../components/DetailsView.svelte';

const SERVER_URL = import.meta.env.VITE_SERVER_URL;
const socket = io(`${SERVER_URL}`, {
  autoConnect: false,
  transports: ['websocket'],
  path: '/chat',
  withCredentials: true
});

socket.on('connect', () => {
  console.log('connected');
});

socket.on('disconnect', () => {
  console.log('disconnected');
});

socket.on('new_message', (payload) => {
  const msg: Message = payload.message;
  const chatOrRoomId = payload.id;
  let current = get(chatStore) ? get(chatStore) : get(roomStore);
  const isCurrent = current && current.id === chatOrRoomId;
  const notificationMsg = `@${msg.sender}: ${msg.text.slice(0, 20)} ${
    msg.text.length > 20 ? '...' : ''
  }`;

  if (isCurrent) {
    current = addMessageToChat(current, msg);
    if (get(chatStore)) {
      chatStore.set(<Chat>current);
      roomStore.set(null);
      changeState('home', current.id, null);
    } else {
      roomStore.set(<Room>current);
      chatStore.set(null);
      changeState('home', null, current.id);
    }
  }

  updateChatList(chatOrRoomId, msg);
  notify
    .fire({
      icon: 'info',
      title: (<Room>current).name,
      text: notificationMsg
    })
    .then((res) => {
      if (res.isConfirmed && !isCurrent) {
        if (payload.type === 'chat') changeState('home', chatOrRoomId, null);
        else if (payload.type === 'room')
          changeState('home', null, chatOrRoomId);

        fetchCurrentChatOrRoom();
        const currentStore = get(chatStore) ? chatStore : roomStore;
        currentStore.update((current) => {
          current.msgCount = 0;

          return current;
        });
      }
    });
});

function newRoomOrRoomUpdate(event: string, payload) {
  fetchUserChats();

  const member =
    payload.member === get(user).username
      ? 'You were'
      : `${payload.member} was`;
  let message = '';
  let showBtn = true;
  let btnText = 'View';
  if (event === 'new') {
    message = `${member} added to ${payload.name} by @${payload.admin}`;
    socket.emit('join_room', { name: payload.id });
  } else if (event === 'update') {
    const current = get(roomStore);

    message = `Room name was changed to ${payload.name} by @${payload.admin}`;
    if (current && current.id === payload.id) {
      roomStore.update((room) => {
        room.name = payload.name;
        return room;
      });
    }
    if (get(state).detailsOn) {
      document.querySelector('#details-popup').remove();
      const detailPopup = new DetailsView({
        target: document.querySelector('.main-section .right'),
        props: {
          details: get(roomStore)
        }
      });
    }
  } else if (event === 'remove') {
    const current = get(roomStore);

    socket.emit('leave_room', { name: payload.id });
    showBtn = false;
    message = `${member} removed from ${payload.name} by @${payload.admin}`;
    if (current && current.id === payload.id) {
      roomStore.set(null);
      changeState('home', null, null);
    }
  }

  notify
    .fire({
      icon: 'info',
      title: payload.name,
      text: message,
      confirmButtonText: btnText,
      showConfirmButton: showBtn
    })
    .then((res) => {
      if (res.isConfirmed) {
        changeState('home', null, payload.id);
        fetchCurrentChatOrRoom();
      }
    });
}

socket.on('add_to_room', newRoomOrRoomUpdate);
socket.on('room_update', newRoomOrRoomUpdate);
socket.on('remove_from_room', newRoomOrRoomUpdate);

socket.on('new_chat', (payload) => {
  fetchUserChats();
  socket.emit('join_room', { name: payload.id });

  notify
    .fire({
      icon: 'info',
      title: `@${payload.texter} messaged you!`,
      confirmButtonText: 'Open'
    })
    .then((res) => {
      if (res.isConfirmed) {
        changeState('home', payload.id, null);
        fetchCurrentChatOrRoom();
      }
    });
});

socket.on('leave_room', (payload) => {
  fetchUserChats();
  const match = <Room>get(activeChats).find((room) => {
    if (room.id === payload.id) return true;
  });

  if (!match) return;

  if (
    get(roomStore) &&
    get(roomStore).id === match.id &&
    get(state).detailsOn
  ) {
    roomStore.update((room) => {
      room.members = room.members.filter((member) => {
        if (member !== payload.member) return true;
      });
      return room;
    });
    document.querySelector('#details-popup').remove();
    const detailPopup = new DetailsView({
      target: getDetailsTarget(),
      props: {
        details: get(roomStore)
      }
    });
  }
  notify.fire({
    icon: 'info',
    title: `${payload.member} left ${match.name}`
  });
});

function addOrRemoveAdmin(event: string, payload) {
  fetchUserChats();

  const current = get(roomStore);
  const isCurrent = current && current.id === payload.id;
  let member =
    payload.member === get(user).username
      ? 'You were'
      : `@${payload.member} was`;
  let message = '';
  if (event === 'grant')
    message = `${member} granted admin privilege by @${payload.admin}`;
  else if (event === 'revoke') {
    member =
      payload.member === get(user).username ? 'Your' : `@${payload.member}'s`;
    message = `${member} admin privilege was revoked by @${payload.admin}`;
  }

  if (isCurrent) {
    roomStore.update((room) => {
      if (event === 'grant') room.admins.push(payload.member);
      else if (event === 'revoke')
        room.admins = room.admins.filter((admin) => {
          if (admin !== payload.member) return true;
        });
      return room;
    });
    if (get(state).detailsOn) {
      document.querySelector('#details-popup').remove();
      const detailPopup = new DetailsView({
        target: document.querySelector('.main-section .right'),
        props: {
          details: get(roomStore)
        }
      });
    }
  }
  notify
    .fire({
      icon: 'info',
      title: payload.name,
      text: message,
      confirmButtonText: 'Open',
      showConfirmButton: true
    })
    .then((res) => {
      if (res.isConfirmed && !isCurrent) {
        changeState('home', null, payload.id);
        fetchCurrentChatOrRoom();
      }
    });
}

socket.on('add_admin', addOrRemoveAdmin);
socket.on('remove_admin', addOrRemoveAdmin);

export default socket;
