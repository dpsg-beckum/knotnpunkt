<script>
	import { onMount } from "svelte";
	import { current_user, current_view } from "./stores.js";
	import Sidebar from "./Sidebar.svelte";
	import Navigation from "./Navigation.svelte";
	import LoginForm from "./LoginForm.svelte";
	import Mainmenu from "./Mainmenu.svelte";
	import RegistrationForm from "./RegistrationForm.svelte";
	import LoadingScreen from "./LoadingScreen.svelte"
	import jQuery from "jquery";
import Profil from "./Profil.svelte";

	onMount(() => {window.jQuery = jQuery;});
	window.printUser = () => {
		console.log($current_user);
	};

	function getUserInfo(event) {
		console.log(event);
		fetch("/api/accountInfo", {
			method: "GET",
			headers: { "Content-Type": "application/json" },
		})
			.then((response) => response.json())
			.then(function (data) {
				$current_user = data.user;
				console.log($current_user);
			})
			.catch((err) => {
				console.log(err);
			});
	}

	function logout(event) {
		fetch("/api/logout", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
		})
			.then((response) => response.json())
			.then(function (data) {
				getUserInfo({details:{origin: "logout"}});
				window.jQuery("#offcanvas").offcanvas("toggle");
			})
			.catch((err) => {
				console.log(err);
			});
	}

	function openProfile(event) {
		$current_view = "loading";
		fetch("/api/benutzer/"+event.detail.benutzername, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        })
            .then((response) => response.json())
            .then(function (data) {
                console.log(data);
				$current_view = {name: "profil", benutzer: data.user};
                // if (data.success == true) {
                //     benutzer = data.user;
                //     if (benutzer.benutzername == $current_user.benutzername) {
                //         edit = true
                //     }
                // } else {
                //     errorMsg = "Ein Fehler ist aufgetreten.";
                // }
            })
            .catch((err) => {
                console.log(err);
            });
		
	}
	
	getUserInfo({details:{origin: "init"}});
	
	$:{if ($current_user.authenticated== false) {
		$current_view = "login";
	}else if ($current_user.authenticated == true){
		$current_view="mainmenu";
	};}
</script>

<Sidebar on:logout={logout} on:openProfile={openProfile}/>
<div class="container-fluid" style="margin-bottom:4em">
	{#if $current_view == "loading"}
		<LoadingScreen/>
	{:else if $current_view == "login"}
		<LoginForm on:getUserInfo={getUserInfo}/>
		<!-- <LoginForm on:getUserInfo={(event)=>{console.log(event)}}/>  -->
	{:else if $current_view == "registration"}
		<RegistrationForm />
	{:else if $current_view == "mainmenu"}
		<Mainmenu />
	{:else if $current_view.name == "profil"}
		<!-- <Profil /> -->
		<Profil benutzer={$current_view.benutzer}/>
	{/if}
</div>
<Navigation />
