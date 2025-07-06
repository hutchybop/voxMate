const status_text = document.querySelector('.status_text');

function checkStatus() {
  fetch("/voxSpotify/check_status")
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json()
    })
    .then(data => {

        console.log(data)

        if (data.status === "user_code") {
            status_text.textContent = "Success"
            setTimeout(() => {
                window.location.href = "/voxSpotify/callback";
            }, 1000);
        } else if (data.status === "user") {
            status_text.textContent = "User not found on the server. \n\n You will now be logged out. Please log back in and try again."
            setTimeout(() => {
                window.location.href = "/logout";
            }, 5000);

        } else if (data.status === "vox") {
            status_text.textContent = "There has been an error. \n\n Clear your session by Logging out of Spotify and try again."
            setTimeout(() => {
                window.location.href = "/voxSpotify/logout";
            }, 5000);

        } else if (data.status === "spotify_error") {
            status_text.textContent = `Error: ${data.error} There has been a Spotify error logging you in.`;
            setTimeout(() => {
                window.location.href = "/voxSpotify";
            }, 5000);

        } else if (data.status === "server_error") {
            status_text.textContent = `Error: ${data.error} There has been a server error logging you in.`;
            setTimeout(() => {
                window.location.href = "/voxSpotify";
            }, 5000);

        } else {
            setTimeout(checkStatus, 2000);  // Check again in 2 seconds
      }
    })
    .catch(err => {
        status_text.textContent = `Error: ${err} A network error occurred. Please try again.`;
        setTimeout(() => {
            window.location.href = "/voxSpotify";
        }, 5000);
    })
}

// Start polling after 25 seconds to give the user chnance to actually login to spotify
setTimeout(() => {
    checkStatus();
}, 25000);
