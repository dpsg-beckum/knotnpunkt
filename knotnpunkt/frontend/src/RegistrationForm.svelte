<script>
import { current_view } from "./stores";

function showLogin(event) {
    $current_view = "login";
}

</script>

<p>Registrierung</p>

<button
    class="btn btn-link link-secondary"
    on:click={showLogin}
    style="font-size: 0.8em">Anmelden</button
>
