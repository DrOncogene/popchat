<script lang="ts">
  import { slide } from 'svelte/transition';
  import { user } from '../lib/store';
  import {
    changeState,
    showFormError,
    validateInput,
    SERVER_URL
  } from '../lib/utils';
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
        if (payload.detail === 'username already exists')
          showFormError('Username already exists', userInput);
        else if (payload.detail === 'email already exists')
          showFormError('Email already exist', emailInput);
        return;
      }
      document.querySelector('#loader').classList.remove('hidden');
      document.querySelector('#loader').classList.add('flex');
      setTimeout(() => {
        user.set(payload.user);
        changeState('login');
      }, 2000);
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
  class="max-w-[1040px] h-full m-auto flex justify-center items-center md:space-x-28"
>
  <div class=" border-r-2 border-r-gray-500 p-8 pr-14 hidden md:block">
    <img src="./img/popchat-logo.png" alt="" width="250" height="250" />
  </div>
  <div
    class="flex flex-col justify-center items-center space-y-2 shadow-2xl p-10 w-[90%] h-max md:h-min md:w-min md:bg-none bg-logo"
    id="register-form"
  >
    <div class="form-cover md:hidden" />
    <div
      class="hidden bg-pri-900 w-full h-full absolute top-0 left-0 items-center justify-center z-[500]"
      id="loader"
    >
      <span class="loader z-[500]" />
    </div>
    <h1 class="text-xl font-bold md:text-2xl z-50 whitespace-nowrap">
      CREATE AN ACCOUNT
    </h1>
    <form
      on:submit={async (e) => {
        await register(e);
      }}
      action="#"
      class="flex flex-col min-w-[300px] m-auto z-50"
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
        errorMsg={[true, 'Username cannot be empty']}
      />
      <FormInput
        placeholder="Email"
        type="email"
        name="email"
        autocomplete="on"
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
        Already have an account?
        <span
          on:click={goToLogin}
          on:keydown={goToLogin}
          class="cursor-pointer text-sec-900 ml-3 hover:border-b hover:border-b-sec-900 not-italic font-semibold"
          >Log in
        </span>
      </p>
    </form>
  </div>
</div>

<style>
</style>
