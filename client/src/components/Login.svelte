<script lang="ts">
  import { slide } from 'svelte/transition';
  import { auth, state, user } from '../lib/store';
  import socket from '../lib/socket';
  import {
    validateInput,
    displayFormError,
    changeState
  } from '../lib/helpers';
  import Button from './Button.svelte';
  import FormInput from './FormInput.svelte';

  const login = async (e) => {
    e.preventDefault();

    const userInput: HTMLInputElement = document.querySelector('#username');
    const passInput: HTMLInputElement = document.querySelector('#password');
    const username = userInput.value;
    const password = passInput.value;

    if (!validateInput(username, password)) {
      return;
    }

    const url = `${import.meta.env.VITE_SERVER_URL}/auth/login`;
    try {
      const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: username,
          password: password
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        displayFormError('Invalid username or password', userInput, passInput);
        return;
      }
      document.querySelector('#loader').classList.remove('hidden');
      document.querySelector('#loader').classList.add('flex');
      document
        .querySelector('#login-form h1, #login-form form')
        .classList.toggle('hidden');
      setTimeout(() => {
        user.set(payload.user);
        // $auth.token = payload.auth;
        // localStorage.setItem('popchat_alx_t', $auth.token);
        changeState('home');
        socket.connect();
      }, 1000);
    } catch (error) {
      displayFormError('Server error, try again later');
    }
  };

  const goToSignUp = (e) => {
    e.preventDefault();
    changeState('register');
  };
</script>

<div in:slide class="max-w-[1040px] h-[500px] m-auto flex justify-center items-center md:space-x-32 p-10">
  <div class=" border-r-2 border-r-gray-500 p-8 hidden md:block">
    <img src="./img/popchat-logo.png" alt="" width="250" height="250">
  </div>
  <div class="relative flex flex-col justify-between items-center space-y-4 shadow-2xl p-10" id="login-form">
    <div class="hidden bg-pri-900 w-full h-full absolute top-0 left-0 items-center justify-center" id="loader">
      <div class="loader">Loading...</div>
    </div>
    <h1 class="text-xl font-bold md:text-2xl">LOGIN TO CONTINUE</h1>
    <form on:submit={async (e) => {await login(e)}} action="#" class="flex flex-col w-[max-content] m-auto">
      <p class="text-red-500 mb-3 w-full text-center text-sm invisible" id="form-errors">An error</p>
      <FormInput
        placeholder='Username'
        type='text'
        name='username'
        errorMsg={[true, 'Enter your username']}
      />
      <FormInput
        placeholder='Password'
        type='password'
        name='password'
        styles='mb-0'
        errorMsg={[true, 'Enter your password']}
      />
      <Button
        text='Log in'
        dim={[2, 2]}
        type='submit'
        styles='bg-sec-900 w-full font-bold mt-10 mb-8'
      />
      <p class="text-center italic font-light text-xs md:text-sm">Don't have an account? <a href="/" on:click={goToSignUp} class="text-[#1FDBA5] ml-3 hover:border-b hover:border-b-[#1FDBA5] not-italic font-semibold">Sign Up</a></p>
    </form>
  </div>
</div>


<style>
  
</style>