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
        avg_cpu=Avg('cpu_usage'),
    )
    vuln_attack = vulnerable_logs.filter(attack_type=attack['key']).aggregate(
        avg_time=Avg('execution_time'),
        avg_ram=Avg('ram_usage'),
        avg_cpu=Avg('cpu_usage'),
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

# Generate bar graphs for each factor
x = range(len(attack_types))
width = 0.35

fig, axes = plt.subplots(3, 1, figsize=(14, 18))

# Execution Time Bar Graph
axes[0].bar([i - width/2 for i in x], [attack_data[atk['key']]['secure_time'] for atk in attack_types], width, label='Secure', color='green')
axes[0].bar([i + width/2 for i in x], [attack_data[atk['key']]['vuln_time'] for atk in attack_types], width, label='Vulnerable', color='red')
axes[0].set_xticks(x)
axes[0].set_xticklabels([atk['name'] for atk in attack_types], rotation=45, ha='right')
axes[0].set_title('Average Execution Time per Attack Type (s)')
axes[0].set_ylabel('Time (s)')
axes[0].legend()

# RAM Usage Bar Graph
axes[1].bar([i - width/2 for i in x], [attack_data[atk['key']]['secure_ram'] for atk in attack_types], width, label='Secure', color='green')
axes[1].bar([i + width/2 for i in x], [attack_data[atk['key']]['vuln_ram'] for atk in attack_types], width, label='Vulnerable', color='red')
axes[1].set_xticks(x)
axes[1].set_xticklabels([atk['name'] for atk in attack_types], rotation=45, ha='right')
axes[1].set_title('Average RAM Usage per Attack Type (MB)')
axes[1].set_ylabel('RAM (MB)')
axes[1].legend()

# CPU Usage Bar Graph
axes[2].bar([i - width/2 for i in x], [attack_data[atk['key']]['secure_cpu'] for atk in attack_types], width, label='Secure', color='green')
axes[2].bar([i + width/2 for i in x], [attack_data[atk['key']]['vuln_cpu'] for atk in attack_types], width, label='Vulnerable', color='red')
axes[2].set_xticks(x)
axes[2].set_xticklabels([atk['name'] for atk in attack_types], rotation=45, ha='right')
axes[2].set_title('Average CPU Usage per Attack Type (%)')
axes[2].set_ylabel('CPU (%)')
axes[2].legend()

plt.tight_layout()

# Save the bar graph image
plt.savefig('sample1.png')
print("Bar graph saved as sample1.png")

plt.close(fig)
