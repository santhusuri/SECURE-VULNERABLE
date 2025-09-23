let lastSeenId = 0;
let soundMuted = false;
let sirenPlaying = false; // track if siren is looping

function showToast(message) {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function playSirenLoop(loop = false) {
    const sound = document.getElementById("alert-sound");
    if (!soundMuted) {
        sound.loop = loop;
        sound.currentTime = 0;
        sound.play().catch(err => console.log("Autoplay blocked:", err));
        sirenPlaying = true;
    }
}

function stopSiren() {
    const sound = document.getElementById("alert-sound");
    sound.pause();
    sound.currentTime = 0;
    sound.loop = false;
    sirenPlaying = false;
}

function highlightRow(row, severity) {
    let color = severity === "high" ? "#ff4c4c" : severity === "medium" ? "#ffc107" : "#28a745";
    row.style.backgroundColor = color;
    setTimeout(() => { row.style.backgroundColor = ""; }, 3000);
}

function animateRow(row) {
    row.style.opacity = 0;
    row.style.transform = "translateX(100%)";
    row.style.transition = "all 0.7s ease";
    setTimeout(() => {
        row.style.opacity = 1;
        row.style.transform = "translateX(0)";
    }, 10);
}

function fetchIncidents() {
    fetch(`/api/incidents/?last_id=${lastSeenId}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector("table tbody");

            data.forEach(incident => {
                // update last seen ID
                lastSeenId = Math.max(lastSeenId, incident.id);

                const severity = (incident.severity || "low").toLowerCase();

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${incident.id}</td>
                    <td>${incident.attack_type}</td>
                    <td>${incident.event_data}</td>
                    <td>${incident.ip_address}</td>
                    <td>${incident.action_taken}</td>
                    <td>${incident.timestamp}</td>
                    <td><span class="severity ${severity}">${incident.severity}</span></td>
                `;
                tbody.prepend(row);

                animateRow(row);
                highlightRow(row, severity);

                if (severity === "high") {
                    showToast(`🚨 High Alert: ${incident.attack_type} from ${incident.ip_address}`);
                    playSirenLoop(true); // continuous loop
                } else if (severity === "medium") {
                    showToast(`⚠️ Medium Alert: ${incident.attack_type}`);
                    playSirenLoop(false); // play once
                } else {
                    showToast(`ℹ️ Low Alert: ${incident.attack_type}`);
                    playSirenLoop(false); // play once
                }
            });
        });
}

// 🔊 Handle mute/unmute toggle
document.addEventListener("DOMContentLoaded", () => {
    const muteBtn = document.getElementById("mute-btn");

    muteBtn.addEventListener("click", () => {
        soundMuted = !soundMuted;
        muteBtn.textContent = soundMuted ? "🔇 Sound Off" : "🔊 Sound On";

        if (soundMuted) {
            stopSiren();
        }
    });

    // Unlock audio on first user click (browser autoplay fix)
    document.addEventListener("click", function initAudio() {
        const audio = document.getElementById("alert-sound");
        audio.play().then(() => {
            audio.pause();
            audio.currentTime = 0;
        }).catch(err => console.log("Autoplay unlock failed:", err));
        document.removeEventListener("click", initAudio);
    });

    fetchIncidents();
    setInterval(fetchIncidents, 5000);
});
