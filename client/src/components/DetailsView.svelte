<script lang="ts">
  import { fly, slide } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import MessageIcon from 'svelte-material-icons/MessageText.svelte';
  import AccountPlus from 'svelte-material-icons/AccountPlus.svelte';
  import MinusIcon from 'svelte-material-icons/Minus.svelte';
  import AccountMinus from 'svelte-material-icons/AccountMinus.svelte';
  import AdminPlusIcon from 'svelte-material-icons/AccountMultiplePlus.svelte';
  import AdminRemoveIcon from 'svelte-material-icons/AccountMultipleRemove.svelte';
  import { user } from '../lib/store';
  import ChatHeader from './ChatHeader.svelte';
  import {
    newChat,
    addOrRemoveMembers,
    addOrRemoveAdmin
  } from '../lib/messaging';
  import {
    ADD_MEMBER,
    REMOVE_MEMBER,
    ADD_ADMIN,
    REMOVE_ADMIN
  } from '../lib/flags';
  import { formatDate } from '../lib/utils';
  import FormInput from './FormInput.svelte';
  import Button from './Button.svelte';

  export let details = null;

  function openForm(e: Event) {
    const toggleBtn = <HTMLButtonElement>(
      document.getElementById('add-member-form-toggle')
    );
    const plus = toggleBtn.querySelector('.open-btn');
    const minus = toggleBtn.querySelector('.close-btn');
    const form = document.getElementById('add-member-form');

    form.classList.toggle('hidden');
    form.classList.toggle('flex');
    plus.classList.toggle('hidden');
    minus.classList.toggle('hidden');
  }
</script>

{#key details}
  {#if details}
    <div
      id="details-popup"
      class="absolute top-0 left-0 h-full w-full lg:px-5 z-[500] flex justify-center items-end bg-transparent backdrop-blur-sm"
    >
      <div
        transition:fly={{ duration: 2000, y: 200 }}
        class="w-full lg:w-5/6 h-5/6 bg-dark-sec overflow-auto backdrop-blur-lg"
      >
        <ChatHeader {details} />
        <div class="p-4">
          {#if 'type' in details && details.type === 'room'}
            <div class="flex flex-col justify-between px-5 pt-5 space-y-3">
              <div class="flex justify-between">
                <h4 class="flex items-center font-bold text-xl">Members</h4>
                {#if details.admins.includes($user.username)}
                  <button
                    on:click={(e) => openForm(e)}
                    id="add-member-form-toggle"
                  >
                    <span title="Add member" class="open-btn"
                      ><AccountPlus size="1.5em" /></span
                    >
                    <span class="close-btn hidden"
                      ><MinusIcon size="1.5em" /></span
                    >
                  </button>
                {/if}
              </div>
              {#if details.admins.includes($user.username)}
                <form
                  id="add-member-form"
                  class="justify-between items-center hidden"
                >
                  <div class="flex flex-col">
                    <FormInput
                      name="add-member-input"
                      styles="rounded-3xl"
                      errorMsg={[true, '']}
                    />
                  </div>
                  <Button
                    dim={[3, 2]}
                    text="Add"
                    type="submit"
                    styles="text-xs font-bold"
                    onClick={(e) => addOrRemoveMembers(e, ADD_MEMBER)}
                  />
                </form>
              {/if}
            </div>
            <ul class="p-5 flex flex-col space-y-3 overflow-hidden flex-nowrap">
              {#each details.members as member (member)}
                {@const currentUserIsCreator =
                  details.creator === $user.username}
                {@const memberIsCreator = details.creator === member}
                {@const memberIsAdmin = details.admins.includes(member)}
                {@const isCurrentUser = member === $user.username}
                {@const currentUserIsAdmin = details.admins.includes(
                  $user.username
                )}
                <li
                  animate:flip
                  transition:slide
                  data-username={member}
                  class="grid grid-flow-col shrink-0"
                >
                  <div class="flex items-center flex-nowrap gap-1">
                    {#if isCurrentUser}
                      You
                    {:else}
                      @{member}
                    {/if}
                    {#if memberIsAdmin}
                      <span
                        class="block self-start text-[8px] py-0.5 px-1 bg-sec-900 rounded-xl w-min justify-self-center"
                        >Admin</span
                      >
                    {/if}
                  </div>
                  {#if !isCurrentUser}
                    <button
                      data-username={member}
                      title="Send message"
                      on:click={(e) => newChat(e)}
                      class="justify-self-center"
                    >
                      <MessageIcon size="1.5em" color="#1FDBA5" />
                    </button>
                    {#if currentUserIsAdmin && !memberIsCreator}
                      {#if currentUserIsCreator && memberIsAdmin}
                        <button
                          data-username={member}
                          title="Remove admin"
                          on:click={(e) => addOrRemoveAdmin(e, REMOVE_ADMIN)}
                          class="justify-self-center"
                        >
                          <AdminRemoveIcon size="1.5em" color="#1FDBA5" />
                        </button>
                      {:else if currentUserIsCreator && !memberIsAdmin}
                        <button
                          data-username={member}
                          title="Make admin"
                          on:click={(e) => addOrRemoveAdmin(e, ADD_ADMIN)}
                          class="justify-self-center"
                        >
                          <AdminPlusIcon size="1.5em" color="#1FDBA5" />
                        </button>
                      {/if}
                      <button
                        on:click={(e) => addOrRemoveMembers(e, REMOVE_MEMBER)}
                        data-username={member}
                        title="Remove member"
                        class="justify-self-end"
                      >
                        <AccountMinus size="1.5em" color="#1FDBA5" />
                      </button>
                    {/if}
                  {/if}
                </li>
              {/each}
            </ul>
          {:else if 'type' in details && details.type === 'chat'}
            <p class="italic text-sm">
              <b>Started on</b>: {formatDate(details.created_at)}
            </p>
          {:else}
            <p class="p-5 flex flex-col">Email: {details.email}</p>
          {/if}
        </div>
      </div>
    </div>
  {/if}
{/key}
