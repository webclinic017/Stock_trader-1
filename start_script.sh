#!/bin/bash
export $(egrep -v '^#' .env | xargs)

echo "#!/bin/bash" > kill_script.sh
if [[ $1 == "master" ]]
then
    (python3 load_balancer.py)& echo "load balancer server running on ${load_balancer_host}:${load_balancer_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
elif [[ $1 == "worker" ]]
then
    (./redis-5.0.8/src/redis-server --port $redis_port)& echo "redis server running on ${redis_host}:${redis_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (python3 trans_server/driver_transserver.py)& echo "trans server running on ${trans_host}:${trans_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (python3 web_server/driver_webserver.py)& echo "web server running on ${web_host}:${web_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (gunicorn --workers=2 --threads=16 --bind="${user_db_host}:${user_db_port}" --chdir=models/user_model user_api:app)& echo "user db server running on ${user_db_host}:${user_db_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (gunicorn --workers=2 --threads=16 --bind="${quote_cache_host}:${quote_cache_port}" --chdir=models/quote_cache quote_cache_api:app)& echo "quote cache server running on ${quote_cache_host}:${quote_cache_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
elif [[ $1 == "audit_logger" ]]
then
    (./redis-5.0.8/src/redis-server --port $redis_port)& echo "redis server running on ${redis_host}:${redis_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (gunicorn --workers=2 --threads=16 --bind="${audit_log_host}:${audit_log_port}" --chdir=models/audit_log_service logger_api:app)& echo "audit log server running on ${audit_log_host}:${audit_log_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
else
    (python3 load_balancer.py)& echo "load balancer server running on ${load_balancer_host}:${load_balancer_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (./redis-5.0.8/src/redis-server --port $redis_port)& echo "redis server running on ${redis_host}:${redis_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (python3 trans_server/driver_transserver.py)& echo "trans server running on ${trans_host}:${trans_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (python3 web_server/driver_webserver.py)& echo "web server running on ${web_host}:${web_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (gunicorn --workers=2 --threads=16 --bind="${user_db_host}:${user_db_port}" --chdir=models/user_model user_api:app)& echo "user db server running on ${user_db_host}:${user_db_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    (gunicorn --workers=2 --threads=16 --bind="${quote_cache_host}:${quote_cache_port}" --chdir=models/quote_cache quote_cache_api:app)& echo "quote cache server running on ${quote_cache_host}:${quote_cache_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
    echo "kill -9 ${!}" >> kill_script.sh
    (gunicorn --workers=2 --threads=16 --bind="${audit_log_host}:${audit_log_port}" --chdir=models/audit_log_service logger_api:app)& echo "audit log server running on ${audit_log_host}:${audit_log_port}, with pid ${!}"
    echo "kill -9 ${!}" >> kill_script.sh
fi