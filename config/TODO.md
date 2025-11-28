# TODO List for Performance Graph and Features

- [x] Create PerformanceLog model to store mode, attack_type, execution_time, ram_usage, cpu_usage, path, method, timestamp.
- [x] Modify core middleware to measure execution time, RAM, CPU usage per request and log to PerformanceLog.
- [x] Enhance middleware to store attack_type detected during request for logging.
- [x] Add performance_dashboard view in orders/views.py to aggregate and graph performance metrics using matplotlib.
- [x] Create performance_dashboard.html template to display graphs and attack-specific performance data.
- [x] Add URL route for performance dashboard in orders/urls.py.
- [x] Test performance logging and dashboard rendering.
- [ ] Optionally add frontend enhancements or filters for dashboard.
- [x] Document new features and usage instructions.

Next Steps:
- Test the middleware logging by running the app and performing actions in both secure and vulnerable modes.
- Access the performance dashboard at /orders/performance/ to verify graphs and data.
- Iterate on UI or data collection as needed.
