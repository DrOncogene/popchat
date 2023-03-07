<script lang="ts">
  import { state, auth, user } from './lib/store'
  import { changeState, fetchUser } from './lib/helpers';
  import socket from './lib/socket'
  import Login from './components/Login.svelte'
  import Home from './components/Home.svelte'
  import RegisterPage from './components/RegisterPage.svelte';

  if ($auth.token && $state.page !== 'login') {
    if ($user.username !== '') {
      socket.connect();
    } else {
      fetchUser();
    }
  } else {
    changeState();
  }
</script>

<main class="md:p-8 w-full h-full">
{#if $state.page === 'register'}
  <RegisterPage />
{:else if $state.page === 'login'}
  <Login />
{:else if $state.page === 'home'}
  <Home />
{/if}
</main>

<style>
  
</style>