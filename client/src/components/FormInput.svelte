<script lang="ts">
  export let placeholder = '';
  export let type = 'text';
  export let value = '';
  export let name: string;
  export let styles = '';
  export let errorMsg = [false, ''];
  export let autocomplete = 'off';
  export let textarea = false;
  export let onKeyUp = (e) => {};

</script>

{#if !textarea}
  <input value="{value}" on:keyup={onKeyUp} placeholder={placeholder} type='{type}' name={name} id={name} class="peer py-2 px-3 rounded-md border border-gray-500 bg-transparent focus:outline focus:outline-1 focus:outline-sec-900 placeholder:text-xs {styles}" required autocomplete={autocomplete} />
  {#if errorMsg[0]}
    <p class="error-p mt-1 mb-3 invisible text-red-500 text-[10px] font-thin peer-invalid:visible">{errorMsg[1]}</p>
  {/if}
{:else}
  <textarea placeholder={placeholder} name={name} id={name} class="peer min-h-[35px] py-2 px-3 rounded-md border border-gray-500 bg-transparent focus:outline focus:outline-1 focus:outline-sec-900 placeholder:text- placeholder:align-middle {styles}" required autocomplete={autocomplete} />
{/if}

<style>
  textarea {
    resize: none;
  }
</style>