import io from "socket.io-client";
import { get } from "svelte/store";
import { activeChats, chatStore, roomStore, user } from '../lib/store';
import { addMessageToChat, changeState, fetchUserChats, updateChatList } from "./helpers";
import notify from "./notify";

const SERVER_URL = import.meta.env.VITE_SERVER_URL;
const socket = io(`${SERVER_URL}`, { autoConnect: false });

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

  if (current && current.id === chatOrRoomId) {
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
  if (current.type === 'chat') {
    notify.info({
      title: 'New message',
      message: `From: @${msg.sender}`,
    });
  } else {
    notify.info({
      title: 'New message',
      message: `In: ${(<Room>current).name} by @${msg.sender}`,
    });
  }
});

socket.on('new_room', (payload) => {
  fetchUserChats();

  setTimeout(() => {
    const match = <Room>get(activeChats).find((chat) => {
      if (chat.id === payload.id) return true;
    });
    if (!match) return;

    socket.emit('join_room', { name: payload.id });
    if (match.created_by === get(user).username) return;

    notify.info({
      title: `You were added to room: ${match.name}`,
    });
  }, 1000);
});

socket.on('remove_from_room', (payload) => {
  fetchUserChats();

  setTimeout(() => {
    const match = <Room>get(activeChats).find((chat) => {
      if (chat.id === payload.id) return true;
    });
    if (!match) return;

    socket.emit('leave_room', { name: payload.id });
    notify.info({
      title: `You were removed from ${match.name}`
    });
  }, 1000);
});

socket.on('new_chat', (payload) => {
  fetchUserChats();
  socket.emit('join_room', { name: payload.id });

  const match = <Chat>get(activeChats).find((chat) => {
    if (chat.id === payload.id) return true;
  });

  const texter = match.user_1 !== get(user).username ? match.user_1 : match.user_2;
  notify.info({
    title: `${texter} started a chat with you`,
  });
});

export default socket;
