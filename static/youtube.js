// YouTube API watch tracking - protect against multiple loads
if (typeof videoWatches === 'undefined') {
    let videoWatches = {};
    let players = [];
    let levelId = null;

    // Extract level_id from URL
    function getLevelId() {
        const path = window.location.pathname;
        const match = path.match(/\/course\/(\w+)/);
        return match ? match[1] : null;
    }

    levelId = getLevelId();

    // Load YouTube IFrame API
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(tag);

    // Called by YouTube API when ready
    function onYouTubeIframeAPIReady() {
        const videoIframes = document.querySelectorAll('.video-embed iframe');
        
        videoIframes.forEach((iframe, index) => {
            const videoId = iframe.src.split('embed/')[1].split('?')[0];
            videoWatches[videoId] = false;
            
            // Replace iframe with div for YT API
            const playerDiv = document.createElement('div');
            playerDiv.id = `youtube-player-${index}`;
            iframe.parentNode.replaceChild(playerDiv, iframe);
            
            // Create player
            const player = new YT.Player(playerDiv, {
                height: '200',
                width: '100%',
                videoId: videoId,
                events: {
                    'onStateChange': onPlayerStateChange
                }
            });
            players.push({ player, videoId });
        });
    }

    // Handle video state changes
    function onPlayerStateChange(event) {
        if (event.data === YT.PlayerState.ENDED) {
            // Find the video ID from the player
            const videoId = event.target.videoId || event.target.getVideoData()?.video_id;
            if (videoId) {
                videoWatches[videoId] = true;
                console.log('Video watched:', videoId);
            }
            checkAllWatched();
        }
    }

    // Check if all videos watched
    function checkAllWatched() {
        const allWatched = Object.values(videoWatches).every(v => v === true);
        
        console.log('Watch status:', videoWatches);
        console.log('All watched:', allWatched);
        
        if (allWatched && levelId) {
            // Mark as watched in backend
            fetch(`/course/${levelId}/mark_watched`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    updateUI();
                    location.reload();
                }
            }).catch(err => console.error('Error marking watched:', err));
        }
    }

    // Update UI after videos watched
    function updateUI() {
        const quizBtn = document.getElementById('quiz-submit-btn');
        const watchAlert = document.getElementById('watch-alert');
        
        if (watchAlert) {
            watchAlert.style.display = 'none';
        }
        if (quizBtn) {
            quizBtn.disabled = false;
            quizBtn.classList.remove('disabled');
        }
        
        console.log('UI updated - quiz unlocked');
    }

    // Check watch status on page load
    document.addEventListener('DOMContentLoaded', function() {
        if (levelId) {
            fetch(`/watch_status/${levelId}`)
                .then(r => r.json())
                .then(data => {
                    console.log('Watch status response:', data);
                    if (data.watched) {
                        updateUI();
                    }
                })
                .catch(err => console.error('Error checking watch status:', err));
        }
    });
}
