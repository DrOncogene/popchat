/// <reference types="svelte" />
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SERVER_URL: string;
  // more env variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

type Paragraph = HTMLParagraphElement;

type Input = HTMLInputElement;

type Message = {
  sender: string;
  when: string;
  text: string;
};

type DayMessages = {
  date: string;
  messages: Message[];
};

type Chat = {
  id: string;
  created_at: string;
  last_msg: Message;
  type: string;
  user_1: string;
  user_2: string;
  messages: DayMessages[];
  msgCount: number = 0;
};

type Room = {
  id: string;
  created_at: string;
  name: string;
  last_msg: Message;
  type: string;
  messages: DayMessages[];
  members: string[];
  admins: string[];
  creator: string;
  updated_at: string;
  msgCount: number;
};

type User = {
  username: string;
  id: string;
  email: string;
};

type State = {
  page: string;
  room: string;
  chat: string;
  detailsOn: boolean;
};

type Payload = {
  message: string;
  status_code: number;
  data: any;
};
