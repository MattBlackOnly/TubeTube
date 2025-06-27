bind = "0.0.0.0:6543"
workers = 1
threads = 4
timeout = 180
preload_app = False
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
