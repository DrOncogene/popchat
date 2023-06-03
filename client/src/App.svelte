<script lang="ts">
  import { onMount } from 'svelte';
  import { state, user } from './lib/store'
  import { fetchUser, loadState } from './lib/helpers';
  import socket from './lib/socket'
  import Login from './components/Login.svelte'
  import Home from './components/Home.svelte'
  import RegisterPage from './components/RegisterPage.svelte';

  loadState();
  onMount(async () => {
    if ($state.page !== 'home') {
      return;
    }
    const userData = await fetchUser();
    user.set(userData);
    if ($user) {
      socket.connect();
    }
  });
</script>

<main class="md:p-8 w-full h-full">
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

<style>
  
</style>