import os
from celery import Celery

# Conectamos Celery a la instancia de Redis que corre en tu Docker
redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "nichehunter_worker",
    broker=redis_url,
    backend=redis_url,
    include=["src.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # En Windows, usar el pool 'solo' evita la corrupción de sockets entre procesos (WinError 10054)
    worker_pool='solo' if os.name == 'nt' else 'prefork',
    
    # Resiliencia de conexión Redis en Windows y Docker
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    redis_backend_always_retry=True,
    redis_socket_keepalive=True,
    redis_socket_timeout=None,
    redis_socket_connect_timeout=30.0,
    broker_transport_options={
        'visibility_timeout': 3600,
        'health_check_interval': 15,
        'max_retries': 5,
    },
    result_backend_transport_options={
        'health_check_interval': 15,
        'retry_policy': {
            'timeout': 10.0,
        }
    }
)


