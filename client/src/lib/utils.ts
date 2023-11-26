import { get } from 'svelte/store';
import { state, user, chatStore, roomStore } from '../lib/store';
import socket from './socket';
import DetailsView from '../components/DetailsView.svelte';

const SERVER_URL = import.meta.env.VITE_SERVER_URL;

function loadState() {
  const savedState = localStorage.getItem('_popchat_state');
  if (!savedState) {
    changeState('login');
    return;
  }
  state.set(JSON.parse(savedState));
}

function saveState() {
  const currState = JSON.stringify(get(state));
  localStorage.setItem('_popchat_state', currState);
}

function changeState(
  page: string = 'login',
  chat: string = null,
  room: string = null,
  detailsOn: boolean = false
) {
  const newState: State = {
    page: page,
    chat: chat,
    room: room,
    detailsOn: detailsOn
  };

  state.set(newState);
  saveState();
}

async function fetchUser() {
  const url = `${SERVER_URL}/api/auth/is_authenticated`;
  try {
    const resp = await fetch(url, {
      credentials: 'include',
      mode: 'cors'
    }).then((res) => res);

    if (resp.status === 200) {
      const payload = await resp.json();
      return payload.data;
    } else {
      changeState('login');
      return null;
    }
  } catch (err) {
    changeState('login');
    return null;
  }
}

async function logout() {
  const url = `${SERVER_URL}/api/auth/logout`;
  const resp = await fetch(url, {
    credentials: 'include'
  });
  if (!resp.ok) {
    changeState('login');
    return;
  }
  changeState('login');
  user.set(null);
  socket.disconnect();
}

function validateInput(
  username: string = null,
  passwd: string = null,
  email: string = null
): boolean {
  const usernameRegex = /^[A-Za-z][A-Za-z0-9]{4,10}$/;
  const passwdRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\.+-=#_%|&@]{7,16}$/;
  const emailRegex =
    /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
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

function getDetailsTarget(): Element {
  let target = document.querySelector('.main-section .right');

  if (!target.classList.contains('right-in') && window.innerWidth < 768) {
    target = document.querySelector('.main-section .left');
  }

  return target;
}

function showDetails(e: Event, type: string = null) {
  e.preventDefault();

  const id = (<HTMLAnchorElement>e.target).parentElement.dataset.id;
  const username = (<HTMLAnchorElement>e.target).parentElement.dataset.username;
  const target = getDetailsTarget();

  document.querySelector('#details-popup')?.remove();

  state.update((state) => {
    state.detailsOn = true;
    return state;
  });

  if (type) {
    const current = get(chatStore) ? get(chatStore) : get(roomStore);

    const detailPopup = new DetailsView({
      target: target,
      props: {
        details: current
      }
    });
    return;
  }
  socket.emit(
    'get_user',
    { id: id, username: username },
    (payload: Payload) => {
      if (payload.status_code !== 200) return;

      const detailPopup = new DetailsView({
        target: target,
        props: {
          details: payload.data
        }
      });
    }
  );
}

function closeDetails(e: Event) {
  e.preventDefault();

  const detailPopup = document.querySelector('#details-popup');
  detailPopup.remove();
  state.update((state) => {
    state.detailsOn = false;
    return state;
  });
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
    year: 'numeric'
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

function switchView(e: Event, openOrClose: string = 'open') {
  e.preventDefault();

  if (window.innerWidth < 768) {
    document.querySelector('.main-section .left').classList.toggle('left-out');
    document.querySelector('.main-section .right').classList.toggle('right-in');
  }

  if (openOrClose === 'close') {
    roomStore.set(null);
    chatStore.set(null);
  }
}

export {
  SERVER_URL,
  loadState,
  saveState,
  changeState,
  fetchUser,
  logout,
  validateInput,
  showFormError,
  getDetailsTarget,
  showDetails,
  closeDetails,
  toggleRoomWidget,
  formatDate,
  switchView
};
