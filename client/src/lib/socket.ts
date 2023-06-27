import io from "socket.io-client";
import { get } from "svelte/store";
import { chatStore, roomStore } from '../lib/store';
import { addMessageToChat, updateChatList } from "./helpers";

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

  if (current.id === chatOrRoomId) {
    current = addMessageToChat(current, msg);
    if (get(chatStore)) {
      // @ts-ignore
      chatStore.set(current);
    } else {
      // @ts-ignore
      roomStore.set(current);
    }
  }

  updateChatList(chatOrRoomId, msg);
});

export default socket;
