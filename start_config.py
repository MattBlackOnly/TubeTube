bind = "0.0.0.0:6543"
workers = 1
threads = 1
timeout = 180
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
