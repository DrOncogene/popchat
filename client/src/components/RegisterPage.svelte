<script lang="ts">
  import { slide, fade } from 'svelte/transition';
  import { state, user } from '../lib/store';
  import {
    changeState,
    showFormError,
    validateInput,
    SERVER_URL
  } from '../lib/helpers';
  import Button from './Button.svelte';
  import FormInput from './FormInput.svelte';

  const register = async (e) => {
    e.preventDefault();

    const userInput: Input = document.querySelector('#username');
    const emailInput: Input = document.querySelector('#email');
    const passInput: Input = document.querySelector('#password');
    const confirmInput: Input = document.querySelector('#confirm-password');

    const username = userInput.value;
    const email = emailInput.value;
    const password = passInput.value;
    const confirm = confirmInput.value;

    if (password !== confirm) {
      showFormError('Password does not match', passInput, confirmInput);
      return;
    }
    if (!validateInput(username, password, email)) {
      return;
    }
    const url = `${SERVER_URL}/api/auth/register`;
    try {
      const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        console.log('An error occurred', payload);
        if (payload.detail === 'username already exists')
          showFormError('Username already exists', userInput);
        else if (payload.detail === 'username already exists')
          showFormError('Email already exist', emailInput);
        return;
      }
      user.set(payload.user);
      $state.page = 'login';
      changeState('login');
    } catch (err) {
      showFormError(`network error: ${err}`);
    }
  };

  const goToLogin = (e) => {
    e.preventDefault();
    changeState('login');
  };
</script>

<div
  in:slide
  class="max-w-[1040px] m-auto flex justify-center items-center md:space-x-28"
>
  <div class=" border-r-2 border-r-gray-500 p-8 pr-14 hidden md:block">
    <img src="./img/popchat-logo.png" alt="" width="250" height="250" />
  </div>
  <div
    class="flex flex-col justify-center items-center space-y-2 shadow-2xl p-10"
  >
    <h1 class="text-xl font-bold md:text-2xl">CREATE AN ACCOUNT</h1>
    <form
      on:submit={async (e) => {
        await register(e);
      }}
      action="#"
      class="flex flex-col min-w-[300px] m-auto"
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
        errorMsg={[true, 'Username cannot be empty']}
      />
      <FormInput
        placeholder="Email"
        type="email"
        name="email"
        errorMsg={[true, 'Enter a valid email addrress']}
      />
      <FormInput
        placeholder="Password"
        type="password"
        name="password"
        errorMsg={[true, 'Password cannot be empty']}
      />
      <FormInput
        placeholder="Confirm password"
        type="password"
        name="confirm-password"
        styles="mb-0"
        errorMsg={[true, 'Password cannot be empty']}
      />
      <Button
        text="Register"
        dim={[2, 2]}
        type="submit"
        styles="bg-sec-900 w-full font-bold mt-6 mb-2"
      />
      <p class="text-center italic font-light text-xs md:text-sm">
        Already have an account? <a
          href="/"
          on:click={(e) => goToLogin(e)}
          class="text-[#1FDBA5] ml-3 hover:border-b hover:border-b-[#1FDBA5] not-italic font-semibold"
          >Log in</a
        >
      </p>
    </form>
  </div>
</div>

<style>
  /* .bg-logo {
    background-image: url('../assets/img/popchat-logo.png');
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    background-clip: padding-box;
  } */
</style>
