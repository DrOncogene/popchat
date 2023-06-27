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

type DayMessages = [day: string, messages: Message[]]

type Chat = {
  id: string;
  name: string;
  last_msg: Message;
  type: string;
  user_1: string,
  user_2: string;
  messages: DayMessages[];
}

type Room = {
  id: string;
  name: string;
  last_msg: Message;
  type: string;
  messages: DayMessages[];
  members: string[];
  admins: string[];
  created_by: string;
  updated_at: string;
}

interface User {
  username: string;
  id: string;
  email: string;
}

interface State {
  page: string;
  room: string;
  chat: string;
}
