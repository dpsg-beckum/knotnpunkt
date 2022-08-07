<script>
	import { onMount } from "svelte";
	import { current_user, current_view } from "./stores.js";
	import Sidebar from "./Sidebar.svelte";
	import Navigation from "./Navigation.svelte";
	import LoginForm from "./LoginForm.svelte";
	import Mainmenu from "./Mainmenu.svelte";
	import RegistrationForm from "./RegistrationForm.svelte";

	import jQuery from 'jquery';

	onMount(() => {window.jQuery = jQuery;	});
</script>

<Sidebar />
<div class="container-fluid" style="margin-bottom:4em">
	{#if $current_view == "login"}
		<LoginForm/>
	{:else if $current_view == "registration"}
		<RegistrationForm/>
	{:else if $current_view == "mainmenu"}
		<Mainmenu />
	{:else if $current_view.name == "profil"}
		<!-- <Profil /> -->
		<p>Profil von {$current_view.user}</p>
	{/if}
</div>
<Navigation />
