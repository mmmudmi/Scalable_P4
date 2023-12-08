# Scalable credit shop
This project implements multiple services designed to offer "Scalable Credit" for sale.

## How to run it
We deploy it through docker
```bash
docker compose build
docker compose up -d
```
## How to test it 
- run `pytest` to run automate testing script
- test file path: Scalable_P4/test/test_simple.py

```bash
cd test
pytest test_simple.py
```
check the database to see the result

## orchestration diagram
![Monitoring Image](images/saga-pattern.jpg)

## Monitoring diagram
![Monitoring Image](images/monitoring.png)
- We use Loki (logging), Jaeger (tracing), Prometheus (Metics) 
- We then use Grafana to bring together data from Loki, Jaeger and Prometheus
### Monitoring Grafana
- Username: admin
- Password: admin 
![Monitoring Image](images/grafana_db.png)
We need to set datasources to specific port
And then connect to dashboard
![setup grafana Image](images/setup_grafana.png)
The dashboard is saved locally. You have to set up for yourself. 
Here is what my grafana dashbord look like after running test_simple.py.

### Monitoring Jaeger
Click [http://localhost:16686/](http://localhost:16686)

### Monitoring Prometheus
Click [http://localhost:9090/](http://localhost:9090/)
These are metrics that we monitor
- order_count_total
- payment_count_total
- payment_rollback_count_total
- inventory_count_total
- inventory_rollback_count_total
- delivery_count_total

## Contributors
- Pearploy Chaicharoensin 6381278 (Mudmee)
- Chiraphat Lua 6381360 (Seowlong)
