import os
import django
import matplotlib.pyplot as plt
import io
import base64

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import PerformanceLog
from django.db.models import Avg

# Define the 8 attack types
attack_types = [
    {'key': 'sql_injection', 'name': 'SQL Injection'},
    {'key': 'xss', 'name': 'XSS'},
    {'key': 'bruteforce', 'name': 'Brute Force'},
    {'key': 'command_injection', 'name': 'Command Injection'},
    {'key': 'malicious_file_upload', 'name': 'Malicious File Upload'},
    {'key': 'directory_traversal', 'name': 'Directory Traversal'},
    {'key': 'session_hijacking', 'name': 'Session Hijacking'},
    {'key': 'csrf_bypass', 'name': 'CSRF Bypass'},
]

# Fetch data
secure_logs = PerformanceLog.objects.filter(mode='secure')
vulnerable_logs = PerformanceLog.objects.filter(mode='vulnerable')

# Prepare data for each attack
attack_data = {}
for attack in attack_types:
    secure_attack = secure_logs.filter(attack_type=attack['key']).aggregate(
        avg_time=Avg('execution_time'),
        avg_ram=Avg('ram_usage'),
        avg_cpu=Avg('cpu_usage')
    )
    vuln_attack = vulnerable_logs.filter(attack_type=attack['key']).aggregate(
        avg_time=Avg('execution_time'),
        avg_ram=Avg('ram_usage'),
        avg_cpu=Avg('cpu_usage')
    )
    attack_data[attack['key']] = {
        'name': attack['name'],
        'secure_time': secure_attack['avg_time'] or 0,
        'vuln_time': vuln_attack['avg_time'] or 0,
        'secure_ram': secure_attack['avg_ram'] or 0,
        'vuln_ram': vuln_attack['avg_ram'] or 0,
        'secure_cpu': secure_attack['avg_cpu'] or 0,
        'vuln_cpu': vuln_attack['avg_cpu'] or 0,
    }

# Generate graph for 8 attacks comparison in secure and vulnerable modes

import matplotlib.pyplot as plt
import io
import base64

fig, ax = plt.subplots(figsize=(14, 8))

# Data for bars
secure_times = [attack_data[atk['key']]['secure_time'] for atk in attack_types]
vuln_times = [attack_data[atk['key']]['vuln_time'] for atk in attack_types]
attack_names = [atk['name'] for atk in attack_types]

x = range(len(attack_types))
width = 0.35

bars1 = ax.bar(x, secure_times, width, label='Secure', color='green')
bars2 = ax.bar([i + width for i in x], vuln_times, width, label='Vulnerable', color='red')

ax.set_xticks([i + width / 2 for i in x])
ax.set_xticklabels(attack_names, rotation=45, ha='right')
ax.set_title('Average Execution Time for 8 Attacks in Secure vs Vulnerable Modes')
ax.set_ylabel('Execution Time (s)')
ax.set_xlabel('Attack Types')
ax.legend()

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.4f}', ha='center', va='bottom')

for bar in bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.4f}', ha='center', va='bottom')

plt.tight_layout()

# Save to file
plt.savefig('8_attacks_secure_vulnerable.png')
print("Graph saved as 8_attacks_secure_vulnerable.png")

# Also save as base64 for potential use
buf = io.BytesIO()
fig.savefig(buf, format='png')
buf.seek(0)
image_base64 = base64.b64encode(buf.read()).decode('utf-8')
buf.close()
plt.close(fig)

# Print base64 (optional)
# print(image_base64)
