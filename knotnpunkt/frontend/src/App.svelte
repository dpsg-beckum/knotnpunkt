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

	function updateUserInfo(){
		fetch("/api/accountInfo", {
				method: "GET",
				headers: { "Content-Type": "application/json" },
			})
				.then((response) => response.json())
				.then(function (data) {
					if (data.user.authenticated == true) {
						$current_view = "mainmenu";
						$current_user = data.user;
					} else {
						$current_view = "login";
					}
				})
				.catch((err) => {
					console.log(err);
				});
	}
	updateUserInfo();
	// console.log($current_user);
</script>

<Sidebar />
<div class="container-fluid" style="margin-bottom:4em">
	{#if $current_view == "login"}
		<LoginForm/>
	{:else if $current_view == "registration"}
		<RegistrationForm/>
	{:else if $current_view == "mainmenu"}
		<Mainmenu />
	{:else if $current_view == "profil"}
		<!-- <Profil /> -->
		<p>Profil von {$current_view.user}</p>
	{/if}
</div>
<Navigation />
