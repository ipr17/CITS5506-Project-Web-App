// Timer functionality
let timerInterval;
let seconds = 0;
const timerDisplay = document.getElementById('timer');
const startTimerBtn = document.getElementById('startTimer');

function updateTimer() {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    timerDisplay.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

startTimerBtn.addEventListener('click', () => {
    if (!timerInterval) {
        timerInterval = setInterval(() => {
            seconds++;
            updateTimer();
            
            // Check for 24-hour alert
            if (seconds === 24 * 3600) {
                document.getElementById('dryingAlert').classList.add('show');
            }
        }, 1000);
        startTimerBtn.textContent = 'Pause Timer';
    } else {
        clearInterval(timerInterval);
        timerInterval = null;
        startTimerBtn.textContent = 'Start Timer';
    }
});

// Manual control functionality
document.getElementById('extendCover').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: 'up' })
        });
        if (response.ok) {
            document.getElementById('coverState').textContent = 'Extended';
        }
    } catch (error) {
        console.error('Error extending cover:', error);
    }
});

document.getElementById('retractCover').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: 'down' })
        });
        if (response.ok) {
            document.getElementById('coverState').textContent = 'Retracted';
        }
    } catch (error) {
        console.error('Error retracting cover:', error);
    }
});

// Update weather symbol based on conditions
function updateWeatherSymbol(condition) {
    const weatherSymbol = document.getElementById('weatherSymbol');
    const symbols = {
        'sunny': '☀️',
        'cloudy': '☁️',
        'rainy': '☔️',
        'snowy': '❄️',
        'partly-cloudy': '⛅️'
    };
    weatherSymbol.textContent = symbols[condition] || '☀️';
}

// Update status functionality
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        document.getElementById('coverState').textContent = data.coverExtended ? 'Extended' : 'Retracted';
        document.getElementById('sunlight').textContent = `${data.sunlight} lux`;
        document.getElementById('rainStatus').textContent = data.rainDetected ? 'Rain Detected' : 'No Rain';
        
        // Update weather symbol
        updateWeatherSymbol(data.weatherCondition);
        
        // Update weather alert
        const weatherAlert = document.getElementById('weatherAlert');
        if (data.rainExpected) {
            weatherAlert.textContent = `Rain expected in ${data.rainHours} hours ☔️`;
            weatherAlert.style.background = 'linear-gradient(135deg, #e6c9a8 0%, #d2b48c 100%)';
        } else {
            weatherAlert.textContent = 'No rain expected in the next 12 hours ☀️';
            weatherAlert.style.background = 'linear-gradient(135deg, var(--accent) 0%, #e6c9a8 100%)';
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Update status every 5 seconds
setInterval(updateStatus, 5000);
updateStatus(); // Initial update

// Add reset timer functionality
document.getElementById('resetTimer').addEventListener('click', () => {
    clearInterval(timerInterval);
    timerInterval = null;
    seconds = 0;
    updateTimer();
    startTimerBtn.textContent = 'Start Timer';
    document.getElementById('dryingAlert').classList.remove('show');
});

function dismissNotification(id) {
    const notification = document.getElementById(id);
    notification.classList.add('fade-out');
    setTimeout(() => {
        notification.style.display = 'none';
    }, 500);
}

function showApiError(message) {
    const toast = document.getElementById('apiError');
    toast.textContent = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 5000);
}

// Emergency button functionality
document.getElementById('emergencyCover').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: 'manualClose' })
        });
        if (response.ok) {
            document.getElementById('coverState').textContent = 'Extended';
        } else {
            showApiError('⚠️ Manual close activation failed');
        }
    } catch (error) {
        showApiError('⚠️ System offline');
    }
});

// Auto-hide drying alert after 5 seconds
setTimeout(() => {
    dismissNotification('dryingAlert');
}, 5000);