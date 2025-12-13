# LernsystemX - Monitoring & Alerting Guide

**Version:** 1.0.0
**Last Updated:** 2025-01-17
**Phase:** 19 - Monitoring & Alerting

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Metrics Collection](#metrics-collection)
4. [Prometheus Setup](#prometheus-setup)
5. [Grafana Dashboards](#grafana-dashboards)
6. [Alerting Rules](#alerting-rules)
7. [Query Examples](#query-examples)
8. [Security](#security)
9. [Troubleshooting](#troubleshooting)

---

## 1. Overview

### Purpose

This monitoring system provides observability for LernsystemX backend operations using Prometheus metrics.

### Goals

- **MTTD < 2 minutes**: Mean Time To Detect issues
- **MTTR < 15 minutes**: Mean Time To Recover from incidents
- **99.9% uptime SLO**: Service Level Objective for API availability
- **p95 < 200ms**: 95th percentile response time under 200ms

### What is Monitored

**HTTP Requests**
- Request count by method, endpoint, status code
- Request duration (latency) with percentiles
- Error rates (4xx client errors, 5xx server errors)

**Business Metrics**
- Analytics events tracked (by type and user role)
- AI method calls (count, duration, tokens, cost)
- Cache operations (hits, misses, errors)

**Infrastructure**
- Database connection pool (active, idle connections)
- Redis operations (count, duration)
- Celery task queue (length, task duration, success/failure)

---

## 2. Architecture

### Components

```
┌─────────────┐         ┌────────────┐         ┌──────────┐
│             │         │            │         │          │
│   Flask     │ ─http─→ │ Prometheus │ ─http─→ │ Grafana  │
│   Backend   │ /metrics│            │         │          │
│             │         │ (Scraper)  │         │  (Viz)   │
└─────────────┘         └────────────┘         └──────────┘
       │                      │
       │                      ↓
       │                ┌────────────┐
       │                │AlertManager│
       ↓                │  (Optional)│
┌─────────────┐         └────────────┘
│   Nginx     │
│   Reverse   │
│    Proxy    │
└─────────────┘
```

### Technology Stack

- **prometheus_client**: Python library for metrics export
- **Prometheus**: Time-series database and metrics collector
- **Grafana**: Visualization and dashboarding
- **AlertManager** (optional): Alert routing and deduplication

---

## 3. Metrics Collection

### HTTP Request Metrics

**lsx_http_requests_total** (Counter)
```python
# Incremented for every HTTP request
Labels: method, endpoint, status_code
Example: lsx_http_requests_total{method="GET", endpoint="/api/courses", status_code="200"}
```

**lsx_http_request_duration_seconds** (Histogram)
```python
# Records request latency with buckets
Labels: method, endpoint
Buckets: 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10 seconds
Example: lsx_http_request_duration_seconds_bucket{method="GET", endpoint="/api/courses", le="0.1"}
```

**lsx_http_errors_total** (Counter)
```python
# Incremented for HTTP errors (4xx, 5xx)
Labels: method, endpoint, error_type
Example: lsx_http_errors_total{method="POST", endpoint="/api/auth/login", error_type="client_error"}
```

### Analytics Metrics

**lsx_analytics_events_total** (Counter)
```python
# Incremented when analytics event is tracked
Labels: event_type, user_type
Example: lsx_analytics_events_total{event_type="course_view", user_type="premium"}
```

### AI Metrics

**lsx_ai_method_calls_total** (Counter)
```python
# Incremented for each AI method call
Labels: method_name, provider
Example: lsx_ai_method_calls_total{method_name="flashcard_generation", provider="anthropic"}
```

**lsx_ai_method_duration_seconds** (Histogram)
```python
# Records AI call duration
Labels: method_name, provider
Buckets: 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60 seconds
```

**lsx_ai_tokens_consumed_total** (Counter)
```python
# Incremented by number of tokens used
Labels: provider, model
```

**lsx_ai_cost_eur_total** (Counter)
```python
# Incremented by cost in EUR
Labels: provider, model
```

**lsx_ai_errors_total** (Counter)
```python
# Incremented on AI call errors
Labels: provider, error_type
```

### Cache Metrics

**lsx_cache_operations_total** (Counter)
```python
# Incremented for cache operations
Labels: operation (get/set/delete), result (hit/miss/success/error)
Example: lsx_cache_operations_total{operation="get", result="hit"}
```

### Database Metrics

**lsx_db_connections_active** (Gauge)
```python
# Current number of active DB connections
```

**lsx_db_connections_idle** (Gauge)
```python
# Current number of idle DB connections
```

**lsx_db_query_duration_seconds** (Histogram)
```python
# Records database query duration
Labels: operation (select/insert/update/delete)
```

### Celery Metrics

**lsx_celery_tasks_total** (Counter)
```python
# Incremented for each Celery task
Labels: task_name, status (success/failure/retry)
```

**lsx_celery_queue_length** (Gauge)
```python
# Current number of tasks waiting in queue
Labels: queue_name
```

---

## 4. Prometheus Setup

### Installation

```bash
# Install Prometheus (Ubuntu/Debian)
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*
```

### Configuration

Create `/etc/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s      # Scrape metrics every 15 seconds
  evaluation_interval: 15s  # Evaluate rules every 15 seconds
  external_labels:
    cluster: 'lsx-production'
    environment: 'production'

# Scrape Configurations
scrape_configs:
  # LernsystemX Backend API
  - job_name: 'lsx_backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s
    # Optional: Basic Auth (if /metrics is protected)
    # basic_auth:
    #   username: 'prometheus'
    #   password: 'SECURE_PASSWORD'

  # PostgreSQL Exporter (optional)
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
    scrape_interval: 30s

  # Redis Exporter (optional)
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
    scrape_interval: 30s

  # Node Exporter (system metrics - optional)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 30s

# Alerting Configuration (optional)
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

# Rule Files
rule_files:
  - '/etc/prometheus/rules/*.yml'
```

### Running Prometheus

```bash
# Create systemd service
sudo nano /etc/systemd/system/prometheus.service
```

```ini
[Unit]
Description=Prometheus Monitoring System
Documentation=https://prometheus.io/docs/introduction/overview/
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus/ \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.enable-lifecycle

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Start Prometheus
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus

# Access Prometheus UI
# http://localhost:9090
```

---

## 5. Grafana Dashboards

### Installation

```bash
# Install Grafana (Ubuntu/Debian)
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Access Grafana UI
# http://localhost:3000 (default: admin/admin)
```

### Add Prometheus Data Source

1. Log in to Grafana (http://localhost:3000)
2. Go to **Configuration** → **Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Set URL: `http://localhost:9090`
6. Click **Save & Test**

### Dashboard Examples

#### API Performance Dashboard

```json
{
  "title": "LernsystemX - API Performance",
  "panels": [
    {
      "title": "Request Rate (req/min)",
      "targets": [
        {
          "expr": "rate(lsx_http_requests_total[1m]) * 60"
        }
      ]
    },
    {
      "title": "Request Duration p95 (ms)",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(lsx_http_request_duration_seconds_bucket[5m])) * 1000"
        }
      ]
    },
    {
      "title": "Error Rate (%)",
      "targets": [
        {
          "expr": "rate(lsx_http_errors_total[5m]) / rate(lsx_http_requests_total[5m]) * 100"
        }
      ]
    },
    {
      "title": "Requests by Endpoint",
      "targets": [
        {
          "expr": "sum(rate(lsx_http_requests_total[5m])) by (endpoint)"
        }
      ]
    }
  ]
}
```

#### AI Operations Dashboard

```json
{
  "title": "LernsystemX - AI Operations",
  "panels": [
    {
      "title": "AI Calls per Minute",
      "targets": [
        {
          "expr": "rate(lsx_ai_method_calls_total[1m]) * 60"
        }
      ]
    },
    {
      "title": "AI Cost per Hour (EUR)",
      "targets": [
        {
          "expr": "rate(lsx_ai_cost_eur_total[1h]) * 3600"
        }
      ]
    },
    {
      "title": "AI Tokens per Minute",
      "targets": [
        {
          "expr": "rate(lsx_ai_tokens_consumed_total[1m]) * 60"
        }
      ]
    },
    {
      "title": "AI Call Duration p95 (seconds)",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(lsx_ai_method_duration_seconds_bucket[5m]))"
        }
      ]
    }
  ]
}
```

#### Cache Performance Dashboard

```json
{
  "title": "LernsystemX - Cache Performance",
  "panels": [
    {
      "title": "Cache Hit Ratio (%)",
      "targets": [
        {
          "expr": "rate(lsx_cache_operations_total{operation=\"get\",result=\"hit\"}[5m]) / (rate(lsx_cache_operations_total{operation=\"get\",result=\"hit\"}[5m]) + rate(lsx_cache_operations_total{operation=\"get\",result=\"miss\"}[5m])) * 100"
        }
      ]
    },
    {
      "title": "Cache Operations per Minute",
      "targets": [
        {
          "expr": "sum(rate(lsx_cache_operations_total[1m])) by (operation) * 60"
        }
      ]
    }
  ]
}
```

---

## 6. Alerting Rules

Create `/etc/prometheus/rules/lsx_alerts.yml`:

```yaml
groups:
  - name: lsx_api_alerts
    interval: 30s
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: |
          rate(lsx_http_errors_total[5m]) / rate(lsx_http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High API error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} over the last 5 minutes."

      # API Down
      - alert: APIDown
        expr: up{job="lsx_backend"} == 0
        for: 1m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "LernsystemX API is down"
          description: "The backend API has been down for more than 1 minute."

      # High Latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, rate(lsx_http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High API latency detected"
          description: "p95 latency is {{ $value }}s (threshold: 0.5s)."

  - name: lsx_ai_alerts
    interval: 60s
    rules:
      # High AI Costs
      - alert: HighAICosts
        expr: |
          rate(lsx_ai_cost_eur_total[1h]) * 3600 > 10
        for: 5m
        labels:
          severity: warning
          component: ai
        annotations:
          summary: "High AI costs detected"
          description: "AI costs are €{{ $value }}/hour (threshold: €10/hour)."

      # AI Error Rate
      - alert: HighAIErrorRate
        expr: |
          rate(lsx_ai_errors_total[5m]) / rate(lsx_ai_method_calls_total[5m]) > 0.1
        for: 3m
        labels:
          severity: warning
          component: ai
        annotations:
          summary: "High AI error rate"
          description: "AI error rate is {{ $value | humanizePercentage }}."

  - name: lsx_cache_alerts
    interval: 60s
    rules:
      # Low Cache Hit Ratio
      - alert: LowCacheHitRatio
        expr: |
          rate(lsx_cache_operations_total{operation="get",result="hit"}[10m]) /
          (rate(lsx_cache_operations_total{operation="get",result="hit"}[10m]) +
           rate(lsx_cache_operations_total{operation="get",result="miss"}[10m])) < 0.5
        for: 5m
        labels:
          severity: warning
          component: cache
        annotations:
          summary: "Low cache hit ratio"
          description: "Cache hit ratio is {{ $value | humanizePercentage }} (threshold: 50%)."

  - name: lsx_database_alerts
    interval: 30s
    rules:
      # High Database Connection Usage
      - alert: HighDBConnectionUsage
        expr: lsx_db_connections_active > 15
        for: 2m
        labels:
          severity: warning
          component: database
        annotations:
          summary: "High database connection usage"
          description: "Active DB connections: {{ $value }} (max: 20)."

  - name: lsx_celery_alerts
    interval: 60s
    rules:
      # Long Celery Queue
      - alert: LongCeleryQueue
        expr: lsx_celery_queue_length > 100
        for: 5m
        labels:
          severity: warning
          component: celery
        annotations:
          summary: "Long Celery task queue"
          description: "Queue length: {{ $value }} tasks (threshold: 100)."
```

---

## 7. Query Examples

### API Queries

**Request rate by endpoint**
```promql
sum(rate(lsx_http_requests_total[5m])) by (endpoint)
```

**p95 latency**
```promql
histogram_quantile(0.95, rate(lsx_http_request_duration_seconds_bucket[5m]))
```

**Error rate percentage**
```promql
rate(lsx_http_errors_total[5m]) / rate(lsx_http_requests_total[5m]) * 100
```

**4xx vs 5xx errors**
```promql
sum(rate(lsx_http_requests_total{status_code=~"4.."}[5m]))
sum(rate(lsx_http_requests_total{status_code=~"5.."}[5m]))
```

### AI Queries

**AI cost per hour by provider**
```promql
sum(rate(lsx_ai_cost_eur_total[1h]) * 3600) by (provider)
```

**AI tokens per minute**
```promql
sum(rate(lsx_ai_tokens_consumed_total[1m]) * 60)
```

**AI call duration p99**
```promql
histogram_quantile(0.99, rate(lsx_ai_method_duration_seconds_bucket[5m]))
```

### Cache Queries

**Cache hit ratio**
```promql
rate(lsx_cache_operations_total{operation="get",result="hit"}[5m]) /
(rate(lsx_cache_operations_total{operation="get",result="hit"}[5m]) +
 rate(lsx_cache_operations_total{operation="get",result="miss"}[5m]))
```

**Cache operations per second**
```promql
sum(rate(lsx_cache_operations_total[1m])) by (operation)
```

---

## 8. Security

### /metrics Endpoint Protection

**Nginx IP Whitelist** (Recommended)
```nginx
location /metrics {
    allow 127.0.0.1;           # Localhost
    allow YOUR_PROMETHEUS_IP;  # Prometheus server
    deny all;
    proxy_pass http://lsx_backend/metrics;
}
```

**Basic Authentication** (Alternative)
```nginx
location /metrics {
    auth_basic "Prometheus Metrics";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://lsx_backend/metrics;
}
```

Create `.htpasswd`:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd prometheus
```

### Sensitive Data in Metrics

**NEVER include in labels:**
- User IDs (high cardinality)
- Email addresses
- Passwords or tokens
- Personal data (GDPR)
- Session IDs

**Safe labels:**
- User role (free/premium/pro)
- Event type
- Endpoint path (normalized)
- HTTP method
- Provider name

---

## 9. Troubleshooting

### /metrics Endpoint Not Accessible

**Check monitoring is enabled:**
```bash
# In backend/.env.production
MONITORING_ENABLED=True
```

**Check Flask app logs:**
```bash
tail -f /var/log/lsx/backend.log | grep -i monitoring
```

**Test endpoint locally:**
```bash
curl http://localhost:8000/metrics
```

### No Metrics Appearing in Prometheus

**Check Prometheus scrape status:**
- Go to http://localhost:9090/targets
- Ensure `lsx_backend` target is "UP"

**Check network connectivity:**
```bash
# From Prometheus server
curl http://BACKEND_IP:8000/metrics
```

**Check Nginx logs:**
```bash
tail -f /var/log/nginx/lsx_error.log
```

### High Memory Usage

Prometheus stores metrics in memory and on disk. Monitor:

```bash
# Check Prometheus disk usage
du -sh /var/lib/prometheus/

# Reduce retention period in prometheus.yml
--storage.tsdb.retention.time=15d
--storage.tsdb.retention.size=10GB
```

### Metrics Reset After Restart

**Counter metrics** (like `_total`) will reset to 0 when Flask restarts. Use `rate()` or `increase()` functions in PromQL which handle this correctly.

---

## Next Steps

1. **Set up Prometheus** - Install and configure Prometheus to scrape /metrics
2. **Create Grafana dashboards** - Build custom dashboards for your team
3. **Configure alerts** - Set up AlertManager for critical alerts
4. **Monitor costs** - Track AI costs and optimize usage
5. **Iterate** - Add custom metrics for your specific business needs

---

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [prometheus_client Python Library](https://github.com/prometheus/client_python)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Dok 30 - LernsystemX Monitoring Architecture](../../LernsystemX-Doku/30_Monitoring-Alerting.md)
