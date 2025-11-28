import os
import django
import matplotlib.pyplot as plt
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import PerformanceLog

# Fetch data
logs = PerformanceLog.objects.filter(attack_type__isnull=False).values('attack_type', 'mode', 'execution_time')

# Convert to DataFrame
df = pd.DataFrame(list(logs))

# Map attack types to readable names
attack_names = {
    'sql_injection': 'SQL Injection',
    'xss': 'XSS',
    'bruteforce': 'Brute Force',
    'command_injection': 'Command Injection',
    'malicious_file_upload': 'Malicious File Upload',
    'directory_traversal': 'Directory Traversal',
    'session_hijacking': 'Session Hijacking',
    'csrf_bypass': 'CSRF Bypass',
}

df['attack_name'] = df['attack_type'].map(attack_names)

# Prepare data for boxplot
attack_types = list(attack_names.values())
secure_data = [df[(df['attack_name'] == atk) & (df['mode'] == 'secure')]['execution_time'].values for atk in attack_types]
vulnerable_data = [df[(df['attack_name'] == atk) & (df['mode'] == 'vulnerable')]['execution_time'].values for atk in attack_types]

# Create box plot
fig, ax = plt.subplots(figsize=(12, 8))
positions = range(len(attack_types))
width = 0.35

# Secure boxes
ax.boxplot(secure_data, positions=positions, widths=width, patch_artist=True, boxprops=dict(facecolor='green'), medianprops=dict(color='black'), showfliers=False, labels=attack_types)

# Vulnerable boxes
ax.boxplot(vulnerable_data, positions=[p + width for p in positions], widths=width, patch_artist=True, boxprops=dict(facecolor='red'), medianprops=dict(color='black'), showfliers=False)

ax.set_title('Execution Time Distribution for Each Attack Type')
ax.set_xlabel('Attack Type')
ax.set_ylabel('Execution Time (s)')
ax.set_xticks([p + width/2 for p in positions])
ax.set_xticklabels(attack_types, rotation=45, ha='right')
ax.legend([plt.Rectangle((0,0),1,1,fc='green'), plt.Rectangle((0,0),1,1,fc='red')], ['Secure', 'Vulnerable'])

plt.tight_layout()

# Save to file
plt.savefig('attack_execution_time_boxplot.png')
print("Graph saved as attack_execution_time_boxplot.png")

plt.close()
