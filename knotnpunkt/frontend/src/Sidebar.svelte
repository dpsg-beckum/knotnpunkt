<script>
    import { current_user, current_view } from "./stores";    
</script>

<div
    class="offcanvas offcanvas-start w-75"
    style="max-width: 17em;"
    id="offcanvas"
    data-bs-keyboard="false"
    data-bs-backdrop="true"
>
    <div class="offcanvas-header">
        {#if $current_user.authenticated}
        <div class="offcanvas-title d-sm-block" id="offcanvas">
            <h6>Herzlich Willkommen,</h6>
            <h5 class="dropdown" style="font-weight: bold;">
                <a
                    href="/"
                    style="color:black"
                    class="nav-link dropdown-toggle p-0"
                    id="dropdown"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                >{$current_user.benutzername}
                    </a
                >
                <ul
                    class="dropdown-menu text-small shadow"
                    aria-labelledby="dropdown"
                >
                    <li>
                        <button class="btn btn-link dropdown-item">Profil</button>
                    </li>

                    <li>
                        <hr class="dropdown-divider" />
                    </li>
                    <li>
                        <button class="btn btn-link dropdown-item">Abmelden</button>
                    </li>
                </ul>
            </h5>
            <h6 style="color: grey;">{$current_user.rolle}</h6>
        </div>
            {/if}
        <button
            type="button"
            class="btn-close text-reset"
            data-bs-dismiss="offcanvas"
            aria-label="Close"
        />
    </div>
    <div class="offcanvas-body px-0">
        <ul
            class="nav nav-pills flex-column mb-sm-auto mb-0 align-items-start"
            id="menu"
        >
        {#if $current_user.authenticated}
        <li class="nav-item">
            <button class="btn btn-link nav-link text-truncate" on:click={e=>{$current_view="mainmenu";window.jQuery('#offcanvas').offcanvas('toggle');}}>
                <i class="fs-5 bi-house">Startseite</i>
            </button>
        </li>
        <li class="nav-item">
            <button class="btn btn-link nav-link text-truncate" on:click={e=>$current_view="registration"}>
                <i class="fs-5 bi-house">Scanner</i>
            </button>
        </li>
            <li class="nav-item">
                <button href="/profil/admin" class="btn btn-link nav-link text-truncate" on:click={e=>$current_view={name: "profil", user: $current_user.benutzername}}>
                    <i class="fs-5 bi-house">Mein Konto</i>
                </button>
            </li>
            <li class="nav-item">
                <button class="btn btn-link nav-link text-truncate">
                    <i class="fs-5 bi-house text-danger">Abmelden</i>
                </button>
            </li>
            {:else}
            <li class="nav-item">
                <button class="btn btn-link nav-link text-truncate">
                    <i class="fs-5 bi-house text-danger">Anmelden</i>
                </button>
            </li>
            <li class="nav-item">
                <button class="btn btn-link nav-link text-truncate">
                    <i class="fs-5 bi-house text-danger">Konto erstellen</i>
                </button>
            </li>
            {/if}
        </ul>
    </div>
</div>
