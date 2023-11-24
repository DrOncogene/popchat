<script lang="ts">
  import { slide } from 'svelte/transition';
  import { user } from '../lib/store';
  import socket from '../lib/socket';
  import {
    validateInput,
    showFormError,
    changeState,
    SERVER_URL
  } from '../lib/utils';
  import Button from './Button.svelte';
  import FormInput from './FormInput.svelte';

  const login = async (e) => {
    e.preventDefault();

    const userInput: HTMLInputElement = document.querySelector('#username');
    const passInput: HTMLInputElement = document.querySelector('#password');
    const username = userInput.value.trim();
    const password = passInput.value.trim();

    if (!validateInput(username, password)) {
      return;
    }

    const url = `${SERVER_URL}/api/auth/login`;
    try {
      const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: username,
          password: password
        })
      });
      if (!response.ok) {
        showFormError('Invalid username or password');
        return;
      }

      const payload = await response.json();
      document.querySelector('#loader').classList.toggle('hidden');
      document.querySelector('#loader').classList.add('flex');
      setTimeout(() => {
        user.set(payload.data);
        socket.auth = { id: $user.id };
        socket.connect();
        changeState('home');
      }, 2000);
    } catch (error) {
      showFormError(`Server error, try again later`);
    }
  };

  const goToSignUp = (e) => {
    e.preventDefault();
    changeState('register');
  };
</script>

<div
  in:slide
  class="max-w-[1040px] h-full m-auto flex justify-center items-center md:space-x-32"
>
  <div class=" border-r-2 border-r-gray-500 p-8 hidden md:block">
    <img src="./img/popchat-logo.png" alt="" width="250" height="250" />
  </div>
  <div
    class="relative flex flex-col justify-center items-center space-y-4 shadow-2xl p-10 w-[90%] h-max md:h-min md:w-min md:bg-none bg-logo"
    id="login-form"
  >
    <div class="form-cover md:hidden" />
    <div
      class="hidden bg-pri-900 w-full h-full absolute top-0 left-0 items-center justify-center z-[500]"
      id="loader"
    >
      <span class="loader z-[500]" />
    </div>
    <h1 class="text-xl font-semibold md:text-2xl whitespace-nowrap z-50">
      LOGIN TO CONTINUE
    </h1>
    <form
      on:submit={async (e) => {
        await login(e);
      }}
      class="flex flex-col w-[max-content] m-auto z-50"
    >
      <p
        class="text-red-500 mb-3 w-full text-center text-sm invisible"
        id="form-errors"
      >
        An error
      </p>
      <FormInput
        placeholder="Username"
        type="text"
        name="username"
        autocomplete="on"
        errorMsg={[true, 'Enter your username']}
      />
      <FormInput
        placeholder="Password"
        type="password"
        name="password"
        styles="mb-0"
        errorMsg={[true, 'Enter your password']}
      />
      <Button
        text="Log in"
        dim={[2, 2]}
        type="submit"
        styles="bg-sec-900 w-full font-bold mt-10 mb-8"
      />
      <p class="text-center italic font-light text-xs md:text-sm">
        Don't have an account? <button
          on:click={goToSignUp}
          on:keydown={goToSignUp}
          tabindex="0"
          class="cursor-pointer text-sec-900 ml-3 hover:border-b hover:border-b-sec-900 not-italic font-semibold"
          >Sign Up</button
        >
      </p>
    </form>
  </div>
</div>

<style>
</style>
