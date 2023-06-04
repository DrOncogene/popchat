import { writable } from "svelte/store";
import type { Writable } from "svelte/store";

const user: Writable<User> = writable(null);

const state: Writable<State> = writable(null);

const activeChats: Writable<(Chat | Room)[]> = writable([]);

const chatStore: Writable<Chat> = writable(null);
const roomStore: Writable<Room> = writable(null);

export {
  user,
  state,
  activeChats,
  chatStore,
  roomStore
};
