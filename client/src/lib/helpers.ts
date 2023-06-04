import { get } from "svelte/store";
import {
  state,
  user,
  activeChats as chatsAndRoomsStore,
  chatStore,
  roomStore } from '../lib/store';
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

function changeState(page: string = 'login', chat: string = null, room: string = null) {
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

function fetchCurrentChatOrRoom () {
  const chatId = get(state).chat;
  const roomId = get(state).room;
  if (chatId) {
    socket.emit('get_chat', {id: chatId}, (payload) => {
      if (payload.status !== 200) return;
      chatStore.set(payload.chat);
    });
  } else if (roomId) {
    socket.emit('get_room', {id: roomId}, (payload) => {
      if (payload.status !== 200) return;
      roomStore.set(payload.room);
    });
  }
}

function fetchUserChats() {
  const userId = get(user).id;
  socket.emit('get_user_chats', {id: userId}, (payload) => {
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
  user.set(null);
  socket.disconnect();
  changeState('login');
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

  if (username && !usernameRegex.test(username)) {
    const userInput = <HTMLInputElement>document.querySelector('#username');
    showFormError('Alphanumeric min 4, max 10', userInput);
    usernameValid = false;
  }
  if (passwd && !passwdRegex.test(passwd)) {
    const passInput = <HTMLInputElement>document.querySelector('#password');
    showFormError('Alphanumeric and .+-=#_%|&@ 7-16 long', passInput);
    passwdValid = false;
  }
  if (email && !emailRegex.test(email)) {
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

  const chatId = (<HTMLAnchorElement>e.target).dataset.id;
  socket.emit('get_chat', {id: chatId}, (payload) => {
    if (payload.status !== 200) return;

    chatStore.set(payload.chat);
    changeState('home', payload.chat.id);
  });
}

function newChat(e: Event) {

}

function showDetails(e: Event, type: string = null) {
  e.preventDefault();

  const id = (<HTMLAnchorElement>e.target).parentElement.dataset.id;
  const target = document.querySelector('.main-section .left');

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
  socket.emit('get_user', { id: id }, (payload) => {
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
  const d = new Date(date);
  if (time) {
    return d.toLocaleTimeString(undefined, {timeStyle: 'short'});
  }

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
    type: get(chatStore) ? 'chat': 'room',
    id: current.id,
    message: message 
  };
  socket.emit('new_message', payload, (data) => {
    if (data.status !== 201) return;

    current = addMessageToChat(current, message);
    if (get(chatStore)) {
      // @ts-ignore
      chatStore.set(current);
    } else {
      // @ts-ignore
      roomStore.set(current);
    }

    updateChatList(current.id, message);
    textInput.value = '';
  });
}

function addMessageToChat (chat: Chat | Room, message: Message) {
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

function updateChatList (chatId: string, message: Message) {
  const chatsAndRooms = get(chatsAndRoomsStore);
  const chatToUpdate = chatsAndRooms.find((chat) => {
    if (chat.id === chatId) return true;
  });

  chatToUpdate.last_msg = message;
  chatsAndRooms.forEach((chat) => {
    if (chat.id === chatId) return chatToUpdate;
    else return chat;
  });

  chatsAndRooms.sort((a, b) => {
    const aDate = new Date(a.last_msg.when);
    const bDate = new Date(b.last_msg.when);
    // @ts-ignore
    return aDate - bDate;
  });
  chatsAndRoomsStore.set(chatsAndRooms);
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
};
