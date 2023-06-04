<script lang="ts">
  import { chatStore, roomStore } from '../lib/store';
  import { sendMessage } from '../lib/helpers';
  import Send from 'svelte-material-icons/Send.svelte';
  import FormInput from './FormInput.svelte';
  import MessageList from './MessageList.svelte';
  import ChatHeader from "./ChatHeader.svelte";
</script>

<ChatHeader />
<div class="w-full min-h-[50vh] flex flex-col justify-center items-center">
  {#if $roomStore || $chatStore}
    <MessageList />
  {/if}
</div>
{#if $roomStore || $chatStore}  
<form on:submit={sendMessage} action="#" class="absolute bottom-0 left-0 min-h-[65px] w-full bg-dark-sec px-3 py-3 flex space-x-3 justify-center items-center" id="new-msg-form">
  <FormInput
    placeholder='Enter a message'
    name='chat-input'
    type='text'
    styles='rounded-3xl px-5 w-3/4'
    textarea={true}
  />
  <button type="submit" class="flex justify-center items-center w-12 h-12 rounded-full bg-pri-900">
    <Send size='1.5em' color='#1FDBA5'/>
  </button>
</form>
{/if}