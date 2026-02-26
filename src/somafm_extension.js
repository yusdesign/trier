// Save this as a bookmark: javascript:(function(){/*paste here*/})();
javascript:(function(){
  const songElement = document.querySelector('.songplaying');
  if(songElement) {
    const song = songElement.textContent;
    fetch('https://your-server.com/log', {
      method: 'POST',
      body: JSON.stringify({
        song: song,
        timestamp: new Date().toISOString(),
        station: 'Indie Pop'
      })
    });
    alert('🎵 Logged: ' + song);
  }
})();
