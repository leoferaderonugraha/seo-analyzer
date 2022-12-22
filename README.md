# SEO Analyzer


## Steps to run

### With docker and docker-compose
Run `docker-compose up` and it's all set.

### Without docker
Run the `run_background_service.sh` before running the `run_web.sh`

### Accessing the web
After the services is started, the web service will show this kind of output:
```
...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:1405
 * Running on http://192.168.0.16:1405
...
```

You can access the web using the `http://192.168.0.16:1405`