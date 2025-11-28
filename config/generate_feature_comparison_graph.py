import matplotlib.pyplot as plt

# Features/tests to compare
features = [
    "SQL Injection (SQLi)",
    "Cross-Site Scripting (XSS)",
    "Cross-Site Request Forgery (CSRF)",
    "File Upload Security",
    "OS-Level Privilege Escalation",
    "Insecure Direct Object Reference (IDOR)",
    "Real-Time Logging",
    "Alert System"
]

# Qualitative scores for Vulnerable Mode (lower is worse)
vulnerable_scores = [1, 1, 1, 1, 1, 1, 3, 3]

# Qualitative scores for Secure Mode (higher is better)
secure_scores = [5, 5, 5, 5, 5, 5, 4, 4]

x = range(len(features))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 7))

# Bar chart for Vulnerable Mode
ax.bar([i - width/2 for i in x], vulnerable_scores, width, label='Vulnerable Mode', color='red')

# Bar chart for Secure Mode
ax.bar([i + width/2 for i in x], secure_scores, width, label='Secure Mode', color='green')

ax.set_xticks(x)
ax.set_xticklabels(features, rotation=45, ha='right')
ax.set_ylabel('Effectiveness / Security Level (1-5)')
ax.set_title('Feature Security Comparison: Vulnerable vs Secure Mode')
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('feature_comparison_bar_chart.png')
print("Feature comparison bar chart saved as feature_comparison_bar_chart.png")
plt.close(fig)
