<script>
	import { current_user } from "./stores.js";
	import Sidebar from "./Sidebar.svelte";
	import Navigation from "./Navigation.svelte";
	import LoginForm from "./LoginForm.svelte";
	import Mainmenu from "./Mainmenu.svelte";


</script>

<Sidebar />
<div class="container-fluid" style="margin-bottom:4em">
	{#if !$current_user.isAuthenticated}
		<LoginForm />
	{:else}
		<Mainmenu/>
	{/if}
</div>
<Navigation />
