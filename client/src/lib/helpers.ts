import { get } from "svelte/store";
import {
  state,
  user,
  activeChats as chatsAndRoomsStore,
  chatStore,
  roomStore
} from '../lib/store';
import socket from "./socket";
import DetailsView from "../components/DetailsView.svelte";

const SERVER_URL = import.meta.env.VITE_SERVER_URL;

function loadState() {
  const savedState = localStorage.getItem('_popchat_state');
  if (!savedState) {
    changeState('login');
    return;
  }
  state.set(JSON.parse(savedState));
};

function saveState() {
  const currState = JSON.stringify(get(state));
  localStorage.setItem('_popchat_state', currState);
};

function changeState(
  page: string = 'login',
  chat: string = null,
  room: string = null) {
  const newState: State = {
    page: page,
    chat: chat,
    room: room
  };

  state.set(newState);
  saveState();
}

async function fetchUser() {
  const url = `${SERVER_URL}/api/auth/is_authenticated`;
  try {
    const resp = await fetch(url,
      {
        credentials: 'include',
        mode: 'cors',
      }).then(res => res);

    if (resp.status === 200) {
      const userData: User = await resp.json();
      return userData;
    } else {
      changeState('login');
      return null;
    }
  } catch (err) {
    changeState('login');
    return null;
  }

}

function fetchCurrentChatOrRoom() {
  const chatId = get(state).chat;
  const roomId = get(state).room;
  if (chatId) {
    socket.emit('get_chat', { id: chatId }, (payload) => {
      if (payload.status !== 200) return;
      chatStore.set(payload.chat);
      roomStore.set(null);
    });
    return;
  }

  socket.emit('get_room', { id: roomId }, (payload) => {
    if (payload.status !== 200) return;
    roomStore.set(payload.room);
    chatStore.set(null);
  });
}

function fetchUserChats() {
  const userId = get(user).id;
  socket.emit('get_user_chats', { id: userId }, (payload) => {
    if (payload.status !== 200) return;
    chatsAndRoomsStore.set(payload.all);
  });
}

async function logout() {
  const url = `${SERVER_URL}/api/auth/logout`;
  const resp = await fetch(url, {
    credentials: 'include',
  });
  if (!resp.ok) {
    console.log('Logout failed');
    return;
  }
  changeState('login', null, null);
  user.set(null);
  socket.disconnect();
}

function validateInput(
  username: string = null,
  passwd: string = null,
  email: string = null): boolean {
  const usernameRegex = /^[A-Za-z][A-Za-z0-9]{4,10}$/;
  const passwdRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\.+-=#_%|&@]{7,16}$/;
  const emailRegex = /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
  let usernameValid = true;
  let passwdValid = true;
  let emailValid = true;

  if (username && !usernameRegex.test(username.trim())) {
    const userInput = <HTMLInputElement>document.querySelector('#username');
    showFormError('Alphanumeric min 4, max 10', userInput);
    usernameValid = false;
  }
  if (passwd && !passwdRegex.test(passwd.trim())) {
    const passInput = <HTMLInputElement>document.querySelector('#password');
    showFormError('Alphanumeric and .+-=#_%|&@ 7-16 long', passInput);
    passwdValid = false;
  }
  if (email && !emailRegex.test(email.trim())) {
    const emailInput = <HTMLInputElement>document.querySelector('#email');
    showFormError('Enter a valid email', emailInput);
    emailValid = false;
  }

  return usernameValid && passwdValid && emailValid;
}

function showFormError(errorMsg: string, ...inputs: Input[]) {
  let errorP: Paragraph = null;

  if (inputs.length === 0) {
    errorP = document.querySelector('#form-errors');
    errorP.textContent = errorMsg;
    errorP.classList.remove('invisible');
    errorP.parentElement.querySelectorAll('input').forEach((input) => {
      input.classList.add('outline');
      input.classList.add('outline-1');
      input.classList.add('outline-red-500');
      input.blur();
    });
    return;
  }

  for (const input of inputs) {
    errorP = document.querySelector(`#${input.id} + .error-p`);
    input.focus();
    input.classList.add('focus:outline-red-500');
    setInterval(() => {
      input.classList.remove('focus:outline-red-500');
    }, 2000);
    errorP.textContent = errorMsg;
    errorP.classList.remove('invisible');
  }
}

function openChat(e: Event) {
  e.preventDefault();

  const target = <HTMLAnchorElement>e.target
  const id = target.dataset.id || target.parentElement.dataset.id
    || target.parentElement.parentElement.dataset.id;
  const type = target.dataset.type || target.parentElement.dataset.type
    || target.parentElement.parentElement.dataset.type;
  const event = type === 'chat' ? 'get_chat' : 'get_room';

  socket.emit(event, { id: id }, (payload) => {
    if (payload.status !== 200) return;

    const detailPopup = document.querySelector('#details-popup');
    if (detailPopup) detailPopup.remove();

    if (type === 'chat') {
      chatStore.set(payload.chat);
      roomStore.set(null);
      changeState('home', payload.chat.id, null);
    } else {
      roomStore.set(payload.room);
      chatStore.set(null);
      changeState('home', null, payload.room.id);
    }

    target.scrollIntoView();
    switchView(e);
  });
}

function newChat(e: Event) {
  const target = <HTMLButtonElement>e.target;
  const username = target.parentElement.dataset.username ||
    target.parentElement.parentElement.dataset.username;

  // @ts-ignore
  const chat: Chat = {
    id: null,
    user_1: get(user).username,
    user_2: username,
    type: 'chat',
    messages: [],
    last_msg: null,
  };

  const chats = get(chatsAndRoomsStore).filter((chat) => {
    return chat.type === 'chat';
  });
  for (const chat of chats) {
    // @ts-ignore
    if (chat.user_1 === username || chat.user_2 === username) {
      // @ts-ignore
      socket.emit('get_chat', { id: chat.id }, (payload) => {
        chatStore.set(payload.chat);
      });
      roomStore.set(null);
      changeState('home', chat.id, null);
      document.querySelector('#details-popup').remove();
      switchView(e);
      return;
    }
  }

  chatStore.set(chat);
  roomStore.set(null);
  changeState('home', null, null);
  document.querySelector('#details-popup').remove();
  switchView(e);
}

function showDetails(e: Event, type: string = null) {
  e.preventDefault();

  const id = (<HTMLAnchorElement>e.target).parentElement.dataset.id;
  const username = (<HTMLAnchorElement>e.target).parentElement.dataset.username;
  let target = document.querySelector('.main-section .right');

  if (!target.classList.contains('right-in') && window.innerWidth < 768) {
    target = document.querySelector('.main-section .left');
  }

  document.querySelector('#details-popup')?.remove();

  if (type) {
    const current = get(chatStore) ? get(chatStore) : get(roomStore);
    if (type === 'chat') current.type = 'chat';
    else current.type = 'room';

    const detailPopup = new DetailsView({
      target: target,
      props: {
        details: current
      }
    });
    return;
  }
  socket.emit('get_user', { id: id, username: username }, (payload) => {
    if (payload.status !== 200) return;

    const detailPopup = new DetailsView({
      target: target,
      props: {
        details: payload.user
      }
    });
  });
}

function closeDetails(e: Event) {
  e.preventDefault();

  const detailPopup = document.querySelector('#details-popup');
  detailPopup.remove();
}

function toggleRoomWidget(e: Event) {
  e.preventDefault();

  document.querySelector('#new-room-widget').classList.toggle('hidden');
}

function formatDate(date: string, time = false) {
  const f = Intl.DateTimeFormat(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',

  });
  const today = new Date();
  const yesterday = new Date(today);
  const d = new Date(date);

  yesterday.setDate(today.getDate() - 1);

  if (time) {
    return d.toLocaleTimeString(undefined, { timeStyle: 'short' });
  }

  if (f.format(d) === f.format(today)) return 'Today';
  if (f.format(d) === f.format(yesterday)) return 'Yesterday';

  return f.format(d);
}

function sendMessage(e: SubmitEvent) {
  e.preventDefault();

  let current = get(chatStore) ? get(chatStore) : get(roomStore);
  const when = new Date().toISOString();
  const textInput = <HTMLInputElement>document.querySelector('#chat-input');

  const message = {
    sender: get(user).username,
    text: textInput.value,
    when: when,
  };

  const payload = {
    type: get(chatStore) ? 'chat' : 'room',
    id: current.id,
    message: message
  };

  if (current.id === null) {
    console.log(current)
    const newChatPayload = {
      creator: get(user).username,
      // @ts-ignore
      user_2: current.user_2,
      message: message,
    };
    socket.emit('create_chat', newChatPayload, (data) => {
      console.log(data)
      if (data.status !== 201) return;

      chatStore.set(data.chat);
      roomStore.set(null);
      changeState('home', data.id, null);
      chatsAndRoomsStore.update((chatsAndRooms) => {
        chatsAndRooms.push(data.chat);
        return chatsAndRooms;
      });
      textInput.value = '';
      textInput.focus();
    });
    return;
  };
  socket.emit('new_message', payload, (data) => {
    if (data.status !== 201) return;

    current = addMessageToChat(current, message);
    if (get(chatStore)) {
      // @ts-ignore
      chatStore.set(current);
      roomStore.set(null);
      changeState('home', current.id, null);
    } else {
      // @ts-ignore
      roomStore.set(current);
      chatStore.set(null);
      changeState('home', null, current.id)
    }

    updateChatList(current.id, message);
    textInput.value = '';
    textInput.focus();
  });
}

function addMessageToChat(chat: Chat | Room, message: Message) {
  let found = false;
  const date = message.when.split('T')[0];

  for (const dayMessage of chat.messages) {
    if (dayMessage[0] === date) {
      dayMessage[1].push(message);
      found = true;
      break;
    }
  }

  if (!found) {
    chat.messages.push([date, [message]]);
  }

  chat.last_msg = message;

  return chat;
}

function updateChatList(chatId: string, message: Message) {
  const chatsAndRooms = get(chatsAndRoomsStore);
  const chatToUpdate = chatsAndRooms.find((chat) => {
    if (chat.id === chatId) return true;
  });

  chatToUpdate.last_msg = message;
  chatsAndRoomsStore.set(
    chatsAndRooms.map((chat) => {
      if (chat.id === chatId) return chatToUpdate;
      else return chat;
    })
  );

  get(chatsAndRoomsStore).sort((a, b) => {
    let aDate: Date, bDate: Date;

    if (!a.last_msg)  {
      aDate = new Date(a.created_at);
    } else {
      aDate = new Date(a.last_msg.when);
    }

    if (!b.last_msg)  {
      bDate = new Date(b.created_at);
    } else {
      bDate = new Date(b.last_msg.when);
    }
    // @ts-ignore
    return aDate - bDate;
  });
}

function addMember(e: Event) {
  e.preventDefault();

  const input = <HTMLInputElement>document.querySelector('#add-member-input');
  const payload = {
    id: get(roomStore).id,
    member: input.value.trim(),
    admin: get(user).username,
    flag: 10,
  };

  socket.emit('add_member', payload, (data) => {
    if (data.status !== 201) {
      showFormError(data.error, input);
      return;
    }

    const room = get(roomStore);
    room.members.push(input.value.trim());
    roomStore.set(data.room);
    input.value = '';

    document.querySelector('#details-popup').remove();
    const detailPopup = new DetailsView({
      target: document.querySelector('.main-section .right'),
      props: {
        details: data.room,
      }
    });
  });
}

function deleteMember(e: Event) {
  const target = <HTMLButtonElement>e.target;
  const username = target.parentElement.dataset.username ||
    target.parentElement.parentElement.dataset.username;

  const payload = {
    id: get(roomStore).id,
    member: username,
    admin: get(user).username,
    flag: 11,
  };

  socket.emit('remove_member', payload, (data) => {
    console.log('REMOVE', data)
    if (data.status !== 201) return;

    const room = get(roomStore);
    room.members.push(username);
    roomStore.set(data.room);

    document.querySelector('#details-popup').remove();
    const detailPopup = new DetailsView({
      target: document.querySelector('.main-section .right'),
      props: {
        details: data.room,
      }
    });
  });
}

function editRoomName(e: Event) {
  e.preventDefault();

  const roomId = (<HTMLButtonElement>e.target)
    .parentElement.parentElement.dataset.id;
  const input = <HTMLInputElement>document.querySelector('#room-name-change');

  const payload = {
    id: roomId,
    name: input.value.trim(),
    admin: get(user).username,
  };
  console.log(payload)

  socket.emit('edit_room_name', payload, (data) => {
    console.log('return', data)
    if (data.status !== 201) return;

    roomStore.set(data.room);

    document.querySelector('#details-popup').remove();
    const detailPopup = new DetailsView({
      target: document.querySelector('.main-section .right'),
      props: {
        details: data.room,
      }
    });
  });
}

function switchView(e: Event) {
  e.preventDefault();

  if (window.innerWidth < 768) {
    document.querySelector('.main-section .left').classList.toggle('left-out');
    document.querySelector('.main-section .right').classList.toggle('right-in');
  }
}

export {
  SERVER_URL,
  loadState,
  saveState,
  changeState,
  fetchUser,
  fetchUserChats,
  fetchCurrentChatOrRoom,
  logout,
  validateInput,
  showFormError,
  showDetails,
  closeDetails,
  openChat,
  newChat,
  toggleRoomWidget,
  formatDate,
  sendMessage,
  addMessageToChat,
  updateChatList,
  addMember,
  deleteMember,
  editRoomName,
  switchView,
};
