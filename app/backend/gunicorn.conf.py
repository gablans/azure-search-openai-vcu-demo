import multiprocessing
import os

max_requests = 1000
max_requests_jitter = 50
log_file = "-"
bind = "0.0.0.0"

timeout = 480  # Increased from 230 for longer AI processing
# https://learn.microsoft.com/troubleshoot/azure/app-service/web-apps-performance-faqs#why-does-my-request-time-out-after-230-seconds

num_cpus = multiprocessing.cpu_count()
if os.getenv("WEBSITE_SKU") == "LinuxFree":
    # Free tier reports 2 CPUs but can't handle multiple workers
    workers = 1
else:
    workers = (num_cpus * 2) + 1
worker_class = "custom_uvicorn_worker.CustomUvicornWorker"
