<script lang="ts">
  import { onMount } from 'svelte';
  import { state, user } from './lib/store';
  import { fetchUser, loadState } from './lib/utils';
  import socket from './lib/socket';
  import Login from './components/Login.svelte';
  import Home from './components/Home.svelte';
  import RegisterPage from './components/RegisterPage.svelte';

  loadState();
  onMount(async () => {
    if ($state.page !== 'home') {
      return;
    }
    const userData = await fetchUser();
    user.set(userData);
    if ($user) {
      socket.auth = { id: $user.id };
      socket.connect();
    }
  });
</script>

<main class="md:p-8 w-full h-full overflow-hidden">
  {#if $state.page === 'register'}
    <RegisterPage />
  {:else if $state.page === 'login'}
    <Login />
  {:else if $state.page === 'home'}
    {#if $user}
      <Home />
    {/if}
  {/if}
</main>
<footer
  class="hidden italic font-thin text-xs opacity-50 w-[100vw] absolute bottom-0 left-0 py-4 md:flex justify-center items-center"
>
  Copyright &copy; 2023 Oncogene Studios
</footer>

<style>
</style>
