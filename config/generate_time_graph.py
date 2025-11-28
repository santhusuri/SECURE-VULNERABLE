import matplotlib.pyplot as plt

# Define the 8 attack types
attacks = [
    'SQL Injection',
    'XSS',
    'Brute Force',
    'Command Injection',
    'Malicious File Upload',
    'Directory Traversal',
    'Session Hijacking',
    'CSRF Bypass'
]

# Example execution times (in seconds) for secure and vulnerable modes
secure_times = [0.05, 0.03, 0.1, 0.08, 0.12, 0.06, 0.04, 0.07]
vulnerable_times = [0.15, 0.12, 0.25, 0.2, 0.3, 0.18, 0.14, 0.22]

# Create bar chart
x = range(len(attacks))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x, secure_times, width, label='Secure', color='green')
ax.bar([i + width for i in x], vulnerable_times, width, label='Vulnerable', color='red')

ax.set_xlabel('Attack Type')
ax.set_ylabel('Execution Time (s)')
ax.set_title('Execution Time of Each Attack Type in Secure and Vulnerable Modes')
ax.set_xticks([i + width / 2 for i in x])
ax.set_xticklabels(attacks, rotation=45, ha='right')
ax.legend()

plt.tight_layout()

# Save as time.png
plt.savefig('time.png')
print("Graph saved as time.png")

plt.close()
