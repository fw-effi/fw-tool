// Check compatibility for the browser we're running this in
if ("serviceWorker" in navigator ) {
  if (navigator.serviceWorker.controller) {
    console.log("[PWA] active service worker found, no need to register");
  } else {
    // Register the service worker
    navigator.serviceWorker
      .register("pwa_service.js", {
        scope: "./"
      })
      .then(function (reg) {
        console.log("[PWA] Service worker has been registered for scope: " + reg.scope);
      });
  }
}

var deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event so it can be triggered later.
  deferredPrompt = e;
  // Update UI notify the user they can install the PWA
  deferredPrompt.prompt();  // Wait for the user to respond to the prompt
});

function showAddToHomeScreen() {
  console.log("[PWA] Show Install Button")
  var installDiv = document.querySelector(".install-app");
  var installBtn = document.querySelector("#installBtn");

  $(".install-app").removeClass("fadeOut"); 
  $(".install-app").addClass("fadeIn");
  installDiv.style.display = "block";

  installBtn.addEventListener("click", addToHomeScreen);

}

function addToHomeScreen() {
  var installDiv = document.querySelector(".install-app");
  var installBtn = document.querySelector("#installBtn");

  $(".install-app").removeClass("fadeIn"); 
  $(".install-app").addClass("fadeOut"); // hide our user interface that shows our A2HS button
  deferredPrompt.prompt();  // Wait for the user to respond to the prompt
  deferredPrompt.userChoice
    .then(function(choiceResult){

  if (choiceResult.outcome === 'accepted') {
    console.log('[PWA]User accepted the Install prompt');
  } else {
    console.log('[PWA]User dismissed the Install prompt');
  }

  deferredPrompt = null;

});}