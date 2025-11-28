let soundMuted = false;
let sirenPlaying = false; // track if siren is looping

// === Toast Notifications ===
function showToast(message) {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// === Sound Control ===
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

// === Row Highlighting ===
function highlightRow(row, severity) {
    let color =
        severity === "critical" ? "#b91c1c" :
        severity === "high" ? "#ef4444" :
        severity === "medium" ? "#facc15" :
        "#22c55e"; // low/others
    row.style.backgroundColor = color;
    setTimeout(() => { row.style.backgroundColor = ""; }, 3000);
}

// === Row Animation ===
function animateRow(row) {
    row.style.opacity = 0;
    row.style.transform = "translateX(100%)";
    row.style.transition = "all 0.7s ease";
    setTimeout(() => {
        row.style.opacity = 1;
        row.style.transform = "translateX(0)";
    }, 10);
}

// === Add new incident row ===
function addIncident(incident) {
    const tableBody = document.getElementById("incident-table-body");
    const lastUpdated = document.getElementById("last-updated");

    const severity = (incident.severity || "low").toLowerCase();

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${incident.id}</td>
      <td>${incident.attack_type}</td>
      <td class="event-data">${incident.event_data}</td>
      <td>${incident.ip_address}</td>
      <td>${incident.action_taken}</td>
      <td>${incident.timestamp}</td>
      <td><span class="badge severity-${severity}">${incident.severity}</span></td>
    `;

    tableBody.prepend(row);

    animateRow(row);
    highlightRow(row, severity);

    // Toast + sound per severity
    if (severity === "critical" || severity === "high") {
        showToast(`🚨 ${incident.severity} Alert: ${incident.attack_type} from ${incident.ip_address}`);
        playSirenLoop(true); // continuous siren
    } else if (severity === "medium") {
        showToast(`⚠️ Medium Alert: ${incident.attack_type}`);
        playSirenLoop(false); // play once
    } else {
        showToast(`ℹ️ Low Alert: ${incident.attack_type}`);
        playSirenLoop(false);
    }

    if (lastUpdated) {
        lastUpdated.textContent = "Last updated: " + new Date().toLocaleTimeString();
    }
}

// === WebSocket Connection ===
document.addEventListener("DOMContentLoaded", function () {
    const muteBtn = document.getElementById("mute-btn");

    // 🔊 Handle mute/unmute toggle
    muteBtn.addEventListener("click", () => {
        soundMuted = !soundMuted;
        muteBtn.textContent = soundMuted ? "🔇 Sound Off" : "🔊 Sound On";
        if (soundMuted) stopSiren();
    });

    // 🔓 Unlock audio on first click (browser autoplay fix)
    document.addEventListener("click", function initAudio() {
        const audio = document.getElementById("alert-sound");
        audio.play().then(() => {
            audio.pause();
            audio.currentTime = 0;
        }).catch(err => console.log("Autoplay unlock failed:", err));
        document.removeEventListener("click", initAudio);
    });

    // Connect WebSocket
    const socket = new WebSocket("ws://" + window.location.host + "/ws/incidents/");

    socket.onmessage = function (e) {
        const incident = JSON.parse(e.data);
        addIncident(incident);
    };

    socket.onclose = function () {
        console.warn("WebSocket closed, attempting reconnect in 5s...");
        setTimeout(() => location.reload(), 5000);
    };
});
