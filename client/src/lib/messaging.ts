import { get } from 'svelte/store';
import socket from './socket';
import {
  user,
  state,
  chatStore,
  roomStore,
  activeChats as chatsAndRoomsStore
} from './store';
import { changeState, showFormError, switchView } from './utils';
import notify from './notify';
import DetailsView from '../components/DetailsView.svelte';
import { ADD_ADMIN, REMOVE_ADMIN, ADD_MEMBER, REMOVE_MEMBER } from './flags';

function fetchUserChats() {
  const userId = get(user).id;
  socket.emit('get_user_chats', { id: userId }, (payload: Payload) => {
    if (payload.status_code !== 200) return;
    chatsAndRoomsStore.set(payload.data);
  });
}

function fetchCurrentChatOrRoom() {
  const chatId = get(state).chat;
  const roomId = get(state).room;
  if (chatId) {
    socket.emit('get_chat', { id: chatId }, (payload: Payload) => {
      if (payload.status_code !== 200) return;
      chatStore.set(payload.data);
      roomStore.set(null);
    });
    return;
  }

  socket.emit('get_room', { id: roomId }, (payload: Payload) => {
    if (payload.status_code !== 200) return;
    roomStore.set(payload.data);
    chatStore.set(null);
  });
}

function openChat(e: Event) {
  e.preventDefault();

  const target = <HTMLAnchorElement>e.target;
  const id =
    target.dataset.id ||
    target.parentElement.dataset.id ||
    target.parentElement.parentElement.dataset.id;
  const type =
    target.dataset.type ||
    target.parentElement.dataset.type ||
    target.parentElement.parentElement.dataset.type;
  const event = type === 'chat' ? 'get_chat' : 'get_room';

  socket.emit(event, { id: id }, (payload) => {
    if (payload.status_code !== 200) return;

    document.querySelector('#details-popup')?.remove();

    updateChatList(id, null);
    if (type === 'chat') {
      chatStore.set(payload.data);
      roomStore.set(null);
      changeState('home', payload.data.id, null);
    } else {
      roomStore.set(payload.data);
      chatStore.set(null);
      changeState('home', null, payload.data.id);
    }

    switchView(e);
  });
}

function newChat(e: Event) {
  const target = <HTMLButtonElement>e.target;
  const username =
    target.parentElement.dataset.username ||
    target.parentElement.parentElement.dataset.username;

  const chat = {
    id: null,
    user_1: get(user).username,
    user_2: username,
    type: 'chat',
    messages: [],
    last_msg: null
  } as Chat;

  const chats = <Chat[]>get(chatsAndRoomsStore).filter((chat) => {
    return chat.type === 'chat';
  });
  for (const chat of chats) {
    if (chat.user_1 === username || chat.user_2 === username) {
      socket.emit('get_chat', { id: chat.id }, (payload: Payload) => {
        chatStore.set(payload.data);
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

function sendMessage(e: SubmitEvent) {
  e.preventDefault();

  let current = get(chatStore) ? get(chatStore) : get(roomStore);
  const when = new Date().toISOString();
  const textInput = <HTMLInputElement>document.querySelector('#chat-input');

  const message = {
    sender: get(user).username,
    text: textInput.value,
    when: when
  };

  const newMessagePayload = {
    type: get(chatStore) ? 'chat' : 'room',
    id: current.id,
    message: message
  };

  if (current.id === null) {
    const newChatPayload = {
      creator: get(user).username,
      user_2: (<Chat>current).user_2,
      message: message
    };
    socket.emit('create_chat', newChatPayload, (payload: Payload) => {
      if (payload.status_code !== 201) {
        notify.fire({
          icon: 'error',
          title: payload.message,
          showConfirmButton: false
        });
        return;
      }

      chatStore.set(payload.data);
      roomStore.set(null);
      changeState('home', payload.data.id, null);
      chatsAndRoomsStore.update((chatsAndRooms) => {
        chatsAndRooms.push(payload.data);
        return chatsAndRooms;
      });
      textInput.value = '';
      textInput.focus();
    });
    return;
  }
  socket.emit('new_message', newMessagePayload, (payload: Payload) => {
    if (payload.status_code !== 201) return;

    current = addMessageToChat(current, message);
    if (get(chatStore)) {
      chatStore.set(<Chat>current);
      roomStore.set(null);
      changeState('home', current.id, null);
    } else {
      roomStore.set(<Room>current);
      chatStore.set(null);
      changeState('home', null, current.id);
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
    if (dayMessage.date === date) {
      dayMessage.messages.push(message);
      found = true;
      break;
    }
  }

  if (!found) {
    chat.messages.push({ date, messages: [message] });
  }

  chat.last_msg = message;

  return chat;
}

function updateChatList(chatId: string, message: Message) {
  const current = get(chatStore) ? get(chatStore) : get(roomStore);
  const isCurrent = current && current.id === chatId;
  const chatsAndRooms = get(chatsAndRoomsStore);
  const chatToUpdate = chatsAndRooms.find((chat) => {
    if (chat.id === chatId) return true;
  });

  if (!message) {
    chatToUpdate.msgCount = 0;
    return;
  }

  chatToUpdate.last_msg = message;
  if (chatToUpdate.msgCount && !isCurrent) {
    chatToUpdate.msgCount += 1;
  } else if (!isCurrent) {
    chatToUpdate.msgCount = 1;
  }

  chatsAndRoomsStore.set(
    chatsAndRooms.map((chat) => {
      if (chat.id === chatId) return chatToUpdate;
      return chat;
    })
  );

  get(chatsAndRoomsStore).sort((a, b) => {
    let aDate: Date, bDate: Date;

    if (!a.last_msg) {
      aDate = new Date(a.created_at);
    } else {
      aDate = new Date(a.last_msg.when);
    }

    if (!b.last_msg) {
      bDate = new Date(b.created_at);
    } else {
      bDate = new Date(b.last_msg.when);
    }

    return aDate.getTime() - bDate.getTime();
  });
}

function addOrRemoveMembers(e: Event, flag: number) {
  e.preventDefault();

  const input = <HTMLInputElement>document.querySelector('#add-member-input');
  const target = <HTMLButtonElement>e.target;
  const sendPayload = {
    id: get(roomStore).id,
    admin: get(user).username,
    flag: flag,
    members: []
  };
  let event;

  if (flag === ADD_MEMBER) {
    if (input.value.trim() in ['', ';']) {
      showFormError('Please enter at least one username', input);
      return;
    }
    event = 'add_member';
    sendPayload.members = input.value
      .split(';')
      .map((s) => s.trim())
      .filter((s) => s !== '');
  } else if (flag === REMOVE_MEMBER) {
    event = 'remove_member';
    const member =
      target.parentElement.dataset.username ||
      target.parentElement.parentElement.dataset.username;
    sendPayload.members = [member];
  }

  let text;
  if (flag === ADD_MEMBER)
    text = `add ${sendPayload.members.map((m) => `@${m}`).join(', ')} to`;
  else if (flag === REMOVE_MEMBER)
    text = `remove ${sendPayload.members.map((m) => `@${m}`).join(', ')} from`;

  notify
    .fire({
      toast: false,
      position: 'center',
      icon: 'question',
      iconColor: 'rgba(31, 219, 165, 0.7)',
      text: `Sure you want to ${text} the room?`,
      timer: 0,
      showConfirmButton: true,
      showCancelButton: true,
      confirmButtonText: 'Yes',
      cancelButtonText: 'No'
    })
    .then((res) => {
      if (!res.isConfirmed) return;

      socket.emit(event, sendPayload, (payload: Payload) => {
        if (payload.status_code !== 200) {
          if (flag === ADD_MEMBER) {
            showFormError(payload.message, input);
          } else if (flag === REMOVE_MEMBER) {
            notify.fire({
              icon: 'error',
              title: payload.message,
              showConfirmButton: false
            });
          }
          return;
        }

        roomStore.set(payload.data);
        input.value = '';

        document.querySelector('#details-popup').remove();
        const detailPopup = new DetailsView({
          target: document.querySelector('.main-section .right'),
          props: {
            details: payload.data
          }
        });
      });
    });
}

function addOrRemoveAdmin(e: Event, flag: number) {
  e.preventDefault();

  const target = <HTMLButtonElement>e.target;
  const sendPayload = {
    id: get(roomStore).id,
    admin: get(user).username,
    flag: flag,
    member:
      target.parentElement.dataset.username ||
      target.parentElement.parentElement.dataset.username
  };

  notify
    .fire({
      toast: false,
      position: 'center',
      icon: 'question',
      iconColor: 'rgba(31, 219, 165, 0.7)',
      text: `Sure you want to ${flag === ADD_ADMIN ? 'add' : 'remove'} @${
        sendPayload.member
      } as admin?`,
      timer: 0,
      showConfirmButton: true,
      showCancelButton: true,
      confirmButtonText: 'Yes',
      cancelButtonText: 'No'
    })
    .then((res) => {
      if (!res.isConfirmed) return;

      let event;
      if (flag === ADD_ADMIN) {
        event = 'add_admin';
      } else if (flag === REMOVE_ADMIN) {
        event = 'remove_admin';
      }

      socket.emit(event, sendPayload, (payload: Payload) => {
        if (payload.status_code !== 200) {
          notify.fire({
            icon: 'error',
            title: payload.message
          });
          return;
        }

        roomStore.set(payload.data);

        document.querySelector('#details-popup').remove();
        const detailPopup = new DetailsView({
          target: document.querySelector('.main-section .right'),
          props: {
            details: payload.data
          }
        });
      });
    });
}

function leaveRoom(e: Event) {
  e.preventDefault();

  notify
    .fire({
      toast: false,
      position: 'center',
      timer: 0,
      icon: 'question',
      iconColor: 'rgba(31, 219, 165, 0.7)',
      title: 'Leave room?',
      showConfirmButton: true,
      showCancelButton: true,
      confirmButtonText: 'Yes',
      cancelButtonText: 'No'
    })
    .then((res) => {
      if (!res.isConfirmed) return;
      const roomName = get(roomStore).name;
      const leaveRoomPayload = {
        room_id: get(roomStore).id,
        id: get(user).id
      };

      socket.emit('exit_room', leaveRoomPayload, (payload: Payload) => {
        if (payload.status_code !== 200) {
          notify.fire({
            icon: 'error',
            title: payload.message,
            showConfirmButton: false
          });
          return;
        }

        roomStore.set(null);
        chatStore.set(null);
        changeState('home', null, null);
        notify.fire({
          icon: 'info',
          title: `You left ${roomName}`,
          showConfirmButton: false
        });
        fetchUserChats();
      });
    });
}

function editRoomName(e: Event) {
  e.preventDefault();

  const roomId = (<HTMLButtonElement>e.target).parentElement.parentElement
    .dataset.id;
  const input = <HTMLInputElement>document.querySelector('#room-name-change');

  const editRoomPayload = {
    id: roomId,
    name: input.value.trim(),
    admin: get(user).username
  };

  socket.emit('edit_room_name', editRoomPayload, (payload) => {
    if (payload.status_code !== 200) return;

    roomStore.set(payload.data);

    document.querySelector('#details-popup').remove();
    const detailPopup = new DetailsView({
      target: document.querySelector('.main-section .right'),
      props: {
        details: payload.data
      }
    });
  });
}

export {
  fetchUserChats,
  fetchCurrentChatOrRoom,
  openChat,
  newChat,
  sendMessage,
  addOrRemoveMembers,
  addOrRemoveAdmin,
  leaveRoom,
  editRoomName,
  updateChatList,
  addMessageToChat
};
