<script>
    import { current_user } from "./stores.js";
</script>

<div class="container">
    <!-- Page Heading -->
    <h1 class="my-4">
        Wilkommen zurück, {current_user.benutzername}
    </h1>

    <div class="row">
        {#each $current_user.apps as app}
            <div class="col-md-3 mb-1">
                <div class="card h-100">
                    <a href="/{app.url}"
                        ><img
                            class="card-img-top"
                            src="img/{app.name}_icon.png"
                            alt={app.titel}
                        /></a
                    >
                    <div class="card-body">
                        <h4 class="card-title">
                            <a href={app.url}>{app.titel}</a>
                        </h4>
                        <p class="card-text">
                            Lorem ipsum dolor sit amet, consectetur adipiscing
                            elit. Nam viverra euismod odio, gravida pellentesque
                            urna varius vitae.
                        </p>
                    </div>
                </div>
            </div>
        {/each}
    </div>
</div>
