<script>
    import { createEventDispatcher } from "svelte";
    import { current_user, current_view } from "./stores.js";
    let benutzername = "";
    let passwort = "";
    let fetching = false;
    let errorMsg = "";
    const dispatch = createEventDispatcher();

    async function handleLogin() {
        fetching = true;
        fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                benutzername: benutzername,
                passwort: passwort,
            }),
        })
            .then((response) => response.json())
            .then(function (data) {
                fetching = false;
                console.log(data);
                if (data.success == true) {
                    dispatch("getUserInfo", {origin: "login"});
                    // $current_view = "mainmenu";

                    // dispatch("login", user);
                } else {
                    errorMsg = "Benutzername oder Passwort falsch.";
                }
            })
            .catch((err) => {
                console.log(err);
            });
    }
    function showRegistration() {
        $current_view = "registration";
    }
</script>

<div class="container-fluid">
    <div class="row mt-5">
        <div class="col-md-4" />
        <div class="col-md-4 d-flex justify-content-center">
            <!-- <img style="width: 10em;" src="img/logo_dpsg_beckum.svg" alt="Logo"> -->
        </div>
        <div class="col-md-4" />
    </div>
    <div class="row mt-4">
        <div class="col-md-4" />
        <div class="col-md-4 d-flex justify-content-center">
            <div class="card">
                <div class="card-body">
                    <div class="card-title text-center">
                        <h1>Anmeldung</h1>
                    </div>
                    <form on:submit|preventDefault={handleLogin}>
                        <input
                            id="csrf_token"
                            name="csrf_token"
                            type="hidden"
                            value="Ijk4OTE0ZjI1ZTIyYzRkNjA2NGFiMDRkZmE3OTdjYjU3MjBhMmVhNjAi.Yu2D-A.f-XrWVPPy22-mCXZNn72EIYVclk"
                        />
                        <div class="row">
                            <div class="col">
                                <label class="form-label" for="user_name"
                                    >Benutzername</label
                                ><br />

                                <input
                                    class="form-control"
                                    id="user_name"
                                    name="user_name"
                                    required
                                    type="text"
                                    bind:value={benutzername}
                                />

                                <br />
                            </div>
                        </div>
                        <div class="row">
                            <div class="col">
                                <label class="form-label" for="password"
                                    >Passwort</label
                                ><br />
                                <input
                                    class="form-control"
                                    id="password"
                                    name="password"
                                    required
                                    type="password"
                                    bind:value={passwort}
                                /><br />
                            </div>
                        </div>
                        <div class="row mt-4">
                            <div class="col text-center">
                                <!-- If there Forms validate()-Function found any errors, render them as Bootstrap-alerts: -->

                                <button
                                    type="submit"
                                    class="btn btn-success"
                                    >Anmelden</button
                                >
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-md-4" />
    </div>
    <div class="row">
        <div class="col-md-4" />
        <div class="col-md-4 d-flex justify-content-center mt-2">
            <div class="">
                <div>
                    <button
                        class="btn btn-link link-secondary"
                        on:click={showRegistration}
                        style="font-size: 0.8em">Neues Konto erstellen</button
                    >
                    {#if fetching == true}
                        <p>Bitte warten...</p>
                    {/if}
                    <p class="test-danger">{errorMsg}</p>
                </div>
            </div>
        </div>
    </div>
</div>
