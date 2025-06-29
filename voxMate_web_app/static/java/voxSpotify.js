function logoutFromSpotify() {
    // Open Spotify logout page in a new tab
    window.open('https://accounts.spotify.com/en/logout', '_blank', 'noopener,noreferrer');

    // Redirect current tab to home
    window.location.href = '/voxSpotify';
}