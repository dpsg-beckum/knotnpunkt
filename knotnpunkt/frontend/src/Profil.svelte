<script>
import { current_user } from "./stores";

export let benutzer = {};
let edit = false;
let errorMsg = "";



</script>

<div class="container">
  <div class="main-body">
    <form action="{benutzer.benutzername}" method="post">
      <div class="row gutters-sm">
       
        <div class="col-md-8 mb-3">
          <div class="card">
            <div class="card-body">

              <div class="row">
                <div class="col-sm-3">
                  <h6 class="mb-0">Benutzername</h6>
                </div>
                <div class="col-sm-9 text-secondary">
                    {#if edit == false}
                  <input class="form-control" type="text" name="benutzername" id="inputBenutzername" placeholder={benutzer.benutzername}
                    value={benutzer.benutzername} readonly>{:else}
                    <input class="form-control" type="text" name="benutzername" id="inputBenutzername" placeholder={benutzer.benutzername}
                    value={benutzer.benutzername}>
                    {/if}
                </div>
              </div>
              
              <hr>
              <div class="row">
                <div class="col-sm-3">
                  <h6 class="mb-0">Name</h6>
                </div>
                <div class="col-sm-9 text-secondary">
                    {#if edit==false}
                    <input class="form-control" type="text" name="name" id="inputBenutzername" value="{benutzer.name}" readonly>
                    {:else}
                         <input class="form-control" type="text" name="name" id="inputBenutzername" value="{benutzer.name}">
                         {/if}
                </div>
              </div>
              <hr>
              <div class="row">
                <div class="col-sm-3">
                  <h6 class="mb-0">Email-Adresse</h6>
                </div>
                <div class="col-sm-9 text-secondary">
                    {#if edit ==false}
                    <input class="form-control" type="text" name="email" id="inputBenutzername" placeholder="{$current_user.emailAdresse}"
                    value="{$current_user.emailAdresse}"readonly>
                    {:else}
                        <input class="form-control" type="text" name="email" id="inputBenutzername" placeholder="{$current_user.emailAdresse}"
                        value="{$current_user.emailAdresse}">
                        {/if}
                </div>
              </div>
              <hr>
              <!-- <div class="row">
                <div class="col-sm-3">
                  <h6 class="mb-0">Rolle</h6>
                </div>
                <div class="col-sm-9 text-secondary">
                  {% if edit  and $current_user.Rolle.name != 'admin'%}
                  <select class="form-control" id="inputRolle" name="rolle">
                    {%for r in roles%}
                    {%if r.name not in ['admin', 'api'] or current_$current_user.Rolle.name == 'admin'%}
                    <option value="{r.name}" {%if $current_user.Rolle.name==r.name %}selected="selected" {%endif%}>{r.name}
                    </option>
                    {%endif%}
                    {%endfor%}
                  </select>
                  {%else%}
                  {$current_user.Rolle.name}
                  {% endif %}
                </div> -->
              </div>
              {#if edit==true}
              <hr>
              <div class="row">
                <div class="col-sm-3">
                  <h6 class="mb-0">Neues Passwort</h6>
                </div>
                <div class="col-sm-9 text-secondary">
                  <input class="form-control" type="password" name="passwort" id="inputBenutzername" placeholder="***"
                    autocomplete="new-password">
                </div>
              </div>
              <div class="row mt-2">
                <div class="col-sm-3">
                  <h6 class="mb-0">Passwort bestätigen</h6>
                </div>
                <div class="col-sm-9 text-secondary">
                  <input class="form-control" type="password" name="passwortBestaetigung" id="inputBenutzername" placeholder="***"
                    autocomplete="new-password">
                </div>
              </div>
              {/if}

              <!-- {% if edit %}
              <div class="row d-none">
                <input type="checkbox" id="checkboxDelete" name="delete">
              </div>
              {% endif %} -->
              {#if errorMsg != ""}
              <div class="row">
                <div class="alert alert-danger">
                  <h6 class="mb-0">{errorMsg}</h6>
                </div>
              </div>
              {/if}
            </div>


          </div>
        </div>

        <!-- <div class="col-md-4">
          <div class="card">
            <div class="card-body">
              <div class="d-flex flex-column align-items-center text-center">
                <div class="row">{%if edit or current_$current_user.name == $current_user.name%}
                <div class="mb-2">
                  <button class="btn btn-primary" type="submit" {% if current_$current_user.benutzername==$current_user.benutzername
                    %}onclick="{alert('Es muss mind. einen Administrator geben.\nSicher dass du deine Benutzerkonto ändern möchtest?')"
                    {%endif%}>Speichern</button>
                    {%endif%}
                {%if edit%}
                  <button class="btn btn-danger" onclick="
                  if(confirm('Sicher, dass du {$current_user.benutzername} löschen möchstes?')){document.getElementById('checkboxDelete').checked = true}">Löschen</button>
                </div>
                {%endif%}
              </div>
                <img src="{url_for('static', filename='avatar_icon.png')}" alt="Admin" class="rounded-circle"
                  width="150">
                <div class="mt-3">
                  <h4>{$current_user.name}</h4>
                  <p class="text-secondary mb-1">{$current_user.Rolle.name}</p>
                  <p class="text-muted font-size-sm">DPSG St. Stephanus Beckum</p>
                </div>
               
              </div>
            </div>
          </div>
        </div> -->
      </div>
    <!-- </form> -->
  </div>

<!-- </div> -->
<!-- </div> -->

