document.addEventListener('DOMContentLoaded', () => {
    const startScreen = document.getElementById('ctf-start-screen');
    const gameScreen = document.getElementById('ctf-game-screen');
    const winScreen = document.getElementById('ctf-win-screen');
    const cooldownScreen = document.getElementById('ctf-cooldown-screen');

    const startBtn = document.getElementById('start-challenge-btn');
    const submitBtn = document.getElementById('submit-flag-btn');
    const flagInput = document.getElementById('flag-input');

    const timeRemainingEl = document.getElementById('time-remaining');
    const attemptsLeftEl = document.getElementById('attempts-left');
    const feedbackBox = document.getElementById('feedback-box');

    const puzzleTitle = document.getElementById('puzzle-title');
    const puzzleDescription = document.getElementById('puzzle-description');
    const cipherType = document.getElementById('cipher-type');
    const puzzleText = document.getElementById('puzzle-text');

    const hint1Btn = document.getElementById('hint1-btn');
    const hint2Btn = document.getElementById('hint2-btn');
    const hintBox = document.getElementById('hint-box');

    let challengeData = null;
    let timerInterval = null;

    async function fetchChallengeData() {
        try {
            const response = await fetch('/api/ctf/ctf-crypto-01');
            if (!response.ok) throw new Error('Failed to load challenge data.');
            challengeData = await response.json();
        } catch (error) {
            console.error(error);
            feedbackBox.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    }

    function displayChallenge() {
        puzzleTitle.textContent = challengeData.title;
        puzzleDescription.textContent = challengeData.description;
        cipherType.textContent = challengeData.cipher_type;
        puzzleText.textContent = challengeData.puzzle;
    }

    function startTimer(durationMinutes) {
        let seconds = durationMinutes * 60;
        timerInterval = setInterval(() => {
            seconds--;
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            timeRemainingEl.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;

            if (seconds <= 0) {
                clearInterval(timerInterval);
                // Handle time up
                gameScreen.style.display = 'none';
                cooldownScreen.style.display = 'block';
                feedbackBox.innerHTML = `<div class="alert alert-danger">Time is up!</div>`;
            }
        }, 1000);
    }

    async function checkStatus() {
        const response = await fetch('/api/ctf/ctf-crypto-01/status');
        const status = await response.json();

        if (status.locked_until) {
            const lockedDate = new Date(status.locked_until);
            if (new Date() < lockedDate) {
                startScreen.style.display = 'none';
                cooldownScreen.style.display = 'block';
                return false;
            }
        }
        return true;
    }

    startBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/ctf/ctf-crypto-01/start', { method: 'POST' });
            if (!response.ok) {
                if (response.status === 429) {
                    feedbackBox.innerHTML = `<div class="alert alert-warning">Cooldown active. Please wait.</div>`;
                    startScreen.style.display = 'none';
                    cooldownScreen.style.display = 'block';
                }
                throw new Error('Could not start challenge.');
            }
            const data = await response.json();

            startScreen.style.display = 'none';
            gameScreen.style.display = 'block';
            
            displayChallenge();
            startTimer(data.time_limit_minutes);
            attemptsLeftEl.textContent = data.attempts_left;

        } catch (error) {
            console.error(error);
            feedbackBox.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    submitBtn.addEventListener('click', async () => {
        const flag = flagInput.value.trim();
        if (!flag) {
            feedbackBox.innerHTML = `<div class="alert alert-warning">Please enter a flag.</div>`;
            return;
        }

        submitBtn.disabled = true;
        feedbackBox.innerHTML = '';

        try {
            const response = await fetch('/api/ctf/ctf-crypto-01/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ flag: flag })
            });
            const result = await response.json();

            if (result.result === 'success') {
                clearInterval(timerInterval);
                gameScreen.style.display = 'none';
                winScreen.style.display = 'block';
            } else {
                attemptsLeftEl.textContent = result.attempts_left;
                let message = 'Incorrect flag. Please try again.';
                if (result.attempts_left <= 0) {
                    message = 'Incorrect flag. You have no attempts left. The challenge is now locked.';
                    clearInterval(timerInterval);
                    gameScreen.style.display = 'none';
                    cooldownScreen.style.display = 'block';
                }
                feedbackBox.innerHTML = `<div class="alert alert-danger">${message}</div>`;
            }
        } catch (error) {
            console.error(error);
            feedbackBox.innerHTML = `<div class="alert alert-danger">An error occurred.</div>`;
        } finally {
            submitBtn.disabled = false;
        }
    });

    hint1Btn.addEventListener('click', () => {
        if (challengeData && challengeData.hints.length > 0) {
            hintBox.textContent = `Hint 1: ${challengeData.hints[0]}`;
            hintBox.style.display = 'block';
            hint1Btn.disabled = true;
        }
    });

    hint2Btn.addEventListener('click', () => {
        if (challengeData && challengeData.hints.length > 1) {
            hintBox.textContent = `Hint 2: ${challengeData.hints[1]}`;
            hintBox.style.display = 'block';
            hint2Btn.disabled = true;
        }
    });

    async function initialize() {
        const isReady = await checkStatus();
        if (isReady) {
            await fetchChallengeData();
        }
    }

    initialize();
});