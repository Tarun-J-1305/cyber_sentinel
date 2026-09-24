// Quiz form validation with progress tracking
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quiz-form');
    const submitBtn = document.getElementById('submit-btn');
    const totalQuestions = form.querySelectorAll('.question-block').length;
    
    function updateProgress() {
        const questionBlocks = form.querySelectorAll('.question-block');
        let answered = 0;
        
        questionBlocks.forEach((block, index) => {
            const checked = form.querySelector(`input[name="q${index}"]:checked`);
            if (checked) {
                answered++;
                block.setAttribute('data-answered', 'true');
                block.style.opacity = '1';
            } else {
                block.setAttribute('data-answered', 'false');
            }
        });
        
        // Update progress bar
        const progressPercent = (answered / totalQuestions) * 100;
        document.getElementById('progress-fill').style.width = progressPercent + '%';
        document.getElementById('answered-count').textContent = answered;
        
        // Enable/disable submit button
        submitBtn.disabled = answered < totalQuestions;
        submitBtn.style.opacity = answered < totalQuestions ? '0.5' : '1';
        submitBtn.style.cursor = answered < totalQuestions ? 'not-allowed' : 'pointer';
        
        return answered === totalQuestions;
    }
    
    if (form) {
        // Check on page load
        updateProgress();
        
        // Check every time a radio button changes
        form.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', function() {
                updateProgress();
                // Add visual feedback
                this.closest('.option').style.backgroundColor = 'rgba(0, 255, 200, 0.1)';
                this.closest('.option').style.transition = 'background-color 0.3s ease';
            });
        });
        
        // Prevent submission if not all answered
        form.addEventListener('submit', function(e) {
            if (!updateProgress()) {
                e.preventDefault();
                alert('Please answer all questions before submitting!');
                submitBtn.focus();
                return false;
            }
        });
    }
});
