/// <reference types="svelte" />
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SERVER_URL: string
  // more env variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

type Paragraph = HTMLParagraphElement;

type Input = HTMLInputElement;

type Message = {
  sender: string;
  when: string;
  text: string;
}

type Chat = {
  id: string;
  name: string;
  last_msg: Message;
  type: string;
  user_1: string,
  user_2: string;
  messages: Message[];
  // members?: string[];
  // admins?: string[];
  // created_by?: string;
  // updated_at?: string;
}

type Room = {
  id: string;
  name: string;
  last_msg: Message;
  type: string;
  messages: Message[];
  members: string[];
  admins: string[];
  created_by: string;
  updated_at: string;
}

interface User {
  username: string;
  // chats: Array<Chat>;
  // rooms: Array<Chat>;
  // all_chats: Array<Chat | Room>;
  id: string;
  email: string;
}

interface State {
  page: string;
  room: string;
  chat: string;
}
