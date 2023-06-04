import { get } from "svelte/store";
import { state, user, activeChats, currentChat } from '../lib/store';
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
  const resp = await fetch(url, 
      {
        credentials: 'include',
        mode: 'cors',
    }).then(res => res)

  if (resp.status === 200) {
    const userData: User = await resp.json();
    return userData;
  } else {
    changeState('login');
    return null;
  }
}

async function fetchChat() {

}

function fetchUserChats() {
  const userId = get(user).id;
  socket.emit('get_user_chats', {id: userId}, (payload) => {
    if (payload.status !== 200) return;
    activeChats.set(payload.all);
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

    currentChat.set(payload.chat);
    changeState('home', payload.chat.id);
  });
}

function newChat(e: Event) {

}

function showDetails(e: Event, type: string = null) {

}

function closeDetails(e: Event) {

}

function toggleWidget(e: Event) {

}

function formatDate(date: string, time = false) {
  const f = Intl.DateTimeFormat(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
  const d = new Date(date);
  if (time) {
    return `${d.toLocaleTimeString(undefined, {timeStyle: 'short'})}`;
  }

  return f.format(d);
}

function sendMessage(e: SubmitEvent) {

}

export {
  SERVER_URL,
  loadState,
  saveState,
  changeState,
  fetchUser,
  fetchUserChats,
  fetchChat,
  logout,
  validateInput,
  showFormError,
  showDetails,
  closeDetails,
  openChat,
  newChat,
  toggleWidget,
  formatDate,
  sendMessage,
};