<script lang="ts">
  import { user, chatStore, roomStore, state } from "../lib/store";
  import { formatDate } from "../lib/helpers";
  import { slide } from "svelte/transition";

  let messages: DayMessages[] = [];

  $: {
    if ($chatStore && $chatStore.messages.length > 0) {
      messages = $chatStore.messages;
    } else if ($roomStore && $roomStore.messages.length > 0) {
      messages = $roomStore.messages;
    } else {
      messages = [];
    }
  };
</script>

<div class="h-[475px] pb-[85px] w-full flex flex-col-reverse overflow-auto" id="message-list">
  {#each [...messages].reverse() as dayMessages}
  {@const day = formatDate(dayMessages[0])}
  <ul transition:slide={{duration:200}} class="w-full flex flex-col items-end">
      <p class="self-center text-center text-xs italic bg-dark-transp px-3 py-2 rounded-lg">{day}</p>
      {#each dayMessages[1] as message}
      {@const time = formatDate(message.when, true)}
        {#if message.sender === $user.username}
          <li class="sent w-full flex flex-col items-end space-y-1 my-2 px-2">
            <p class="max-w-[60%] p-4 flex justify-center items-center bg-msg-blue rounded-2xl rounded-tr-none text-sm whitespace-pre-line">{message.text}</p>
            <div class="text-[10px] tracking-wider leading-loose font-extralight mr-4">
              <span class="mr-2">{time}</span>
            </div>
          </li>
        {:else}
          <li class="received w-full flex flex-col items-start space-y-1 my-2 self-start px-2">
            <p class="max-w-[60%] p-4 flex justify-center items-center bg-dark-sec rounded-2xl rounded-tl-none text-sm whitespace-pre-line">{message.text}</p>
            <div class="text-[10px] italic font-thin text-right ml-4 whitespace-nowrap text-ellipsis">
              <span class="mr-2">{time}</span>
              <span class="">{message.sender}</span>
            </div>
          </li>
        {/if}
      {/each}
    </ul>
  {/each}
  </div>

<style>
  
</style>