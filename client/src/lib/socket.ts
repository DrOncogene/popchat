import io from "socket.io-client";
import { get } from "svelte/store";
import { activeChats, chatStore, roomStore } from '../lib/store';
import { addMessageToChat, changeState, fetchUserChats, updateChatList } from "./helpers";

const SERVER_URL = import.meta.env.VITE_SERVER_URL;
const socket = io(`${SERVER_URL}`, { autoConnect: false });

socket.on('connect', () => {
  console.log('connected');
});

socket.on('disconnect', () => {
  console.log('disconnected');
});

socket.on('new_message', (payload) => {
  const msg = payload.message;
  const chatOrRoomId = payload.id;
  let current = get(chatStore) ? get(chatStore) : get(roomStore);

  if (current && current.id === chatOrRoomId) {
    current = addMessageToChat(current, msg);
    if (get(chatStore)) {
      // @ts-ignore
      chatStore.set(current);
      roomStore.set(null);
      changeState('home', current.id, null);
    } else {
      // @ts-ignore
      roomStore.set(current);
      chatStore.set(null);
      changeState('home', null, current.id);
    }
  }

  updateChatList(chatOrRoomId, msg);
});

socket.on('new_room', (payload) => {
  fetchUserChats();

  setTimeout(() => {
    const match = get(activeChats).find((chat) => {
      if (chat.id === payload.id) return true;
    });
    if (!match) return;

    socket.emit('join_room', { name: payload.id });
  }, 1000);
});

socket.on('remove_from_room', (payload) => {
  fetchUserChats();

  setTimeout(() => {
    const match = get(activeChats).find((chat) => {
      if (chat.id === payload.id) return true;
    });
    if (!match) return;

    socket.emit('leave_room', { name: payload.id });
  }, 1000);
});

socket.on('new_chat', (payload) => {
  fetchUserChats();
  socket.emit('join_room', { name: payload.id });
});

export default socket;
