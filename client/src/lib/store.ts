import { writable } from "svelte/store";
import type { Writable } from "svelte/store";

const user: Writable<User> = writable(null);

const state: Writable<State> = writable(null);

const activeChats: Writable<(Chat | Room)[]> = writable([]);

const currentChat: Writable<Chat> = writable(null);
const currentRoom: Writable<Room> = writable(null);
const currentDetail: Writable<User | Chat | Room> = writable(null);

export {
  user,
  state,
  activeChats,
  currentChat,
  currentDetail,
  currentRoom
};
