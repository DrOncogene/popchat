<script lang="ts">
  import { fly, slide } from "svelte/transition";
  import { flip } from "svelte/animate";
  import MessageIcon from "svelte-material-icons/MessageText.svelte";
  import PlusIcon from "svelte-material-icons/Plus.svelte";
  import MinusIcon from "svelte-material-icons/Minus.svelte";
  import DeleteIcon from "svelte-material-icons/Delete.svelte";
  import { user } from "../lib/store";
  import ChatHeader from "./ChatHeader.svelte";
  import { formatDate, newChat, addMember, deleteMember } from "../lib/helpers";
  import FormInput from "./FormInput.svelte";
  import Button from "./Button.svelte";

  export let details = null;

  function openForm(e: Event) {
    const toggleBtn = <HTMLButtonElement>document
      .getElementById("add-member-form-toggle");
    const plus = toggleBtn.querySelector(".open-btn");
    const minus = toggleBtn.querySelector(".close-btn");
    const form = document.getElementById("add-member-form");

    form.classList.toggle("hidden");
    plus.classList.toggle("hidden");
    minus.classList.toggle("hidden");
  }
</script>

{#key details}
{#if details}
<div id="details-popup" class="absolute top-0 left-0 h-full w-full px-5 z-[500] flex justify-center items-end bg-transparent backdrop-blur-sm">
  <div transition:fly={{ duration: 2000, y: 200 }} class="w-5/6 h-5/6 bg-dark-sec overflow-auto backdrop-blur-lg">
    <ChatHeader details={ details } />
    <div class="p-4">
      {#if 'type' in details && details.type === 'room'}
      <div class="flex flex-col justify-between px-5 pt-5 space-y-3">
        <div class="flex justify-between">
          <h4 class="flex items-center font-bold text-xl">Members</h4>
          {#if details.admins.includes($user.username)}
          <button on:click={(e) => openForm(e)} id='add-member-form-toggle'>
            <span class="open-btn"><PlusIcon size='1.5em'/></span>
            <span class="close-btn hidden"><MinusIcon size='1.5em'/></span>
          </button>
          {/if}
        </div>
        {#if details.admins.includes($user.username)}
        <form id="add-member-form" class="flex justify-between items-center hidden">
          <div>
            <FormInput
              name='add-member-input'
              styles='rounded-3xl'
              errorMsg={[true, '']}
            />
          </div>
          <Button 
            dim={[3, 2]}
            text='Add'
            type='submit'
            styles='text-xs font-bold'
            onClick = {(e) => addMember(e)}
          />
        </form>
        {/if}
      </div>
      <ul class="p-5 flex flex-col space-y-3 overflow-hidden">
        {#each details.members as member (member)}
          <li animate:flip transition:slide data-username={member} class="grid grid-cols-3 items-center justify-center shrink-0">
            {#if member !== $user.username}  
              @{member}
            {:else}
              You
            {/if}
            {#if details.admins.includes(member)}
              <span class="text-xs py-1 px-2 bg-sec-900 rounded-xl w-min justify-self-center">Admin</span>
            {/if}
            {#if member !== $user.username}
            <button data-username={member} title="Send message" on:click={(e) => newChat(e) } class="justify-self-center">
              <MessageIcon size="1.5em" color="#1FDBA5" />
            </button>
            {/if}
            {#if !details.admins.includes(member) && details.admins.includes($user.username)}
              <button on:click={deleteMember} data-username="{member}" title="Delete Member" class="justify-self-end">
                <DeleteIcon size='1.5em' color='#1FDBA5'/>
              </button>
            {/if}
          </li>
        {/each}
      </ul>
      {:else if 'type' in details && details.type === 'chat' }
        <p class="italic text-sm"><b>Started on</b>:  {formatDate(details.created_at)}</p>
      {:else}
      <p class="p-5 flex flex-col">Email: {details.email}</p>
      {/if}
    </div>
  </div>
</div>
{/if}
{/key}
