<script lang="ts">
  export let text = '';
  export let dim: number[];
  export let type: 'submit' | 'button' = 'button';
  export let styles = '';
  export let title = '';
  export let onClick = (e) => {};

  const size = `px-${dim[0]} py-${dim[1]}`;
</script>

<button
  on:click={onClick}
  {title}
  {type}
  class="rounded-md bg-sec-700 {size} {styles} hover:bg-sec-700"
>
  {text}
  <slot />
</button>

<style>
</style>
