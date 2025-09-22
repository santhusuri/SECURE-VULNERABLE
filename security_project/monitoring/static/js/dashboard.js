let seenIncidents = new Set();
let soundMuted = false;

function showToast(message) {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function playAlertSound() {
    if(!soundMuted){
        const sound = document.getElementById("alert-sound");
        sound.currentTime = 0;
        sound.play();
    }
}

function highlightRow(row, severity) {
    let color = severity=="High" ? "#ff4c4c" : severity=="Medium" ? "#ffc107" : "#28a745";
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
    fetch("/api/incidents/")
    .then(res => res.json())
    .then(data => {
        const tbody = document.querySelector("table tbody");
        data.reverse().forEach(incident => {
            if(!seenIncidents.has(incident.id)){
                seenIncidents.add(incident.id);
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${incident.id}</td>
                    <td>${incident.attack_type}</td>
                    <td>${incident.event_data}</td>
                    <td>${incident.ip_address}</td>
                    <td>${incident.action_taken}</td>
                    <td>${incident.timestamp}</td>
                    <td>${incident.severity}</td>
                `;
                tbody.prepend(row);
                animateRow(row);
                highlightRow(row, incident.severity);

                if(incident.severity=="High") {
                    showToast(`🚨 High Alert: ${incident.attack_type} from ${incident.ip_address}`);
                    playAlertSound();
                } else if(incident.severity=="Medium") {
                    showToast(`⚠️ Medium Alert: ${incident.attack_type}`);
                } else {
                    showToast(`ℹ️ Low Alert: ${incident.attack_type}`);
                }
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    fetchIncidents();
    setInterval(fetchIncidents, 5000);
});
