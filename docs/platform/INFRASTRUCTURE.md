# Infrastructure Setup Guide

This guide walks through setting up the ArbFinder Suite infrastructure using Pulumi.

## Prerequisites

- Pulumi CLI installed (`curl -fsSL https://get.pulumi.com | sh`)
- PostgreSQL database accessible
- Cloudflare account with Zone ID and Account ID
- AWS account (optional)
- Python 3.9+

## Quick Start

### 1. Install Dependencies

```bash
cd infrastructure/pulumi
pip install pulumi pulumi-postgresql pulumi-cloudflare pulumi-aws
```

### 2. Configure Pulumi Stack

```bash
# Create a new stack
pulumi stack init dev

# Set configuration values
pulumi config set environment development
pulumi config set domain arbfinder.example.com

# PostgreSQL configuration
pulumi config set postgresql:host your-db-host.com
pulumi config set postgresql:port 5432
pulumi config set postgresql:username admin
pulumi config set postgresql:password --secret your-db-password
pulumi config set postgresql:database arbfinder

# Application passwords
pulumi config set db_app_password --secret app-password
pulumi config set db_readonly_password --secret readonly-password

# Cloudflare configuration
pulumi config set cloudflare:zone_id your-zone-id
pulumi config set cloudflare:account_id your-account-id

# AWS configuration (optional)
pulumi config set aws:enabled false
pulumi config set aws:region us-east-1
```

### 3. Deploy Infrastructure

```bash
# Preview changes
pulumi preview

# Deploy
pulumi up
```

### 4. Apply Database Migrations

After deployment, apply the database schema:

```bash
# Connect to your PostgreSQL database
psql postgresql://arbfinder_app:password@host:5432/arbfinder

# Run migration script
\i database/migrations/001_initial_schema.sql
```

## Configuration Details

### PostgreSQL Setup

The infrastructure creates:
- Main database: `arbfinder`
- Application user: `arbfinder_app` (full access)
- Read-only user: `arbfinder_readonly` (analytics queries)

#### Connection Strings

```bash
# Application connection
postgresql://arbfinder_app:password@host:5432/arbfinder

# Read-only connection
postgresql://arbfinder_readonly:password@host:5432/arbfinder
```

### Cloudflare Setup

The infrastructure creates:
- D1 Database: Edge caching for frequently accessed data
- R2 Bucket: Object storage for images and metadata
- Worker: Data ingestion endpoint at `api.{domain}/ingest/*`

#### Worker Endpoints

- `POST /api/ingest` - Ingest new item data
- `GET /api/items` - Retrieve cached items
- `GET /api/health` - Health check

### AWS Resources (Optional)

When `aws:enabled` is set to `true`, creates:
- VPC with public subnets
- ECS Cluster for containerized services
- ECR Repository for Docker images
- S3 Bucket for backups with lifecycle policies
- CloudWatch Log Group
- SNS Topic for alerts
- Security Groups

## Database Schema

The database schema includes:

### Core Tables
- `items` - Main inventory tracking
- `price_history` - Audit log of price changes
- `comparable_sales` - Historical sales data
- `market_statistics` - Aggregated market metrics
- `item_metadata_history` - Version control for metadata

### Analysis Tables
- `damage_assessments` - Damage tracking with price impact
- `depreciation_models` - Configurable depreciation curves
- `price_adjustments` - Audit log of adjustments

### User Tables
- `user_watchlists` - User item monitoring
- `search_queries` - Search analytics

### System Tables
- `data_ingestion_log` - Import tracking and statistics

### Views
- `v_active_items_metrics` - Active items with calculated metrics
- `v_market_trends` - Market trends by category
- `v_price_performance` - Price discount analysis

### Materialized Views
- `mv_category_statistics` - Pre-aggregated category stats (refresh periodically)

## Maintenance Tasks

### Backup Database

```bash
# Using pg_dump
pg_dump -h host -U arbfinder_app -d arbfinder -F c -f backup.dump

# Store in S3/R2
aws s3 cp backup.dump s3://arbfinder-backups/$(date +%Y%m%d)/
```

### Refresh Materialized Views

```sql
-- Refresh category statistics
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_statistics;
```

### Optimize Database

```sql
-- Vacuum and analyze
VACUUM ANALYZE;

-- Reindex if needed
REINDEX DATABASE arbfinder;
```

### Monitor Resource Usage

```bash
# Get stack outputs
pulumi stack output

# Check CloudWatch logs (if using AWS)
aws logs tail /arbfinder/dev --follow

# Check Cloudflare analytics
# Visit Cloudflare dashboard
```

## Scaling Considerations

### Vertical Scaling
- Increase PostgreSQL instance size
- Add more CPU/memory to ECS tasks
- Upgrade R2 storage tier

### Horizontal Scaling
- Add read replicas for PostgreSQL
- Scale ECS service task count
- Use multiple Cloudflare Workers regions

### Performance Optimization
- Enable connection pooling (PgBouncer)
- Implement query caching
- Add database partitioning
- Use CDN for static assets

## Monitoring

### Database Monitoring

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

### Application Monitoring

If using AWS:
- CloudWatch Metrics: CPU, Memory, Network
- CloudWatch Logs: Application logs
- X-Ray: Distributed tracing
- SNS: Alerts and notifications

## Troubleshooting

### Connection Issues

```bash
# Test PostgreSQL connection
psql postgresql://user:pass@host:5432/arbfinder -c "SELECT 1"

# Check Cloudflare Worker status
curl https://api.example.com/api/health
```

### Performance Issues

```sql
-- Find long-running queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Kill long-running query
SELECT pg_terminate_backend(pid);
```

### Deployment Issues

```bash
# Check Pulumi state
pulumi stack

# View recent updates
pulumi history

# Rollback if needed
pulumi rollback
```

## Security Best Practices

1. **Secrets Management**
   - Use `--secret` flag for sensitive configs
   - Rotate passwords regularly
   - Use AWS Secrets Manager/Vault for production

2. **Network Security**
   - Use VPC with private subnets
   - Enable SSL/TLS for all connections
   - Implement security groups/firewall rules

3. **Access Control**
   - Follow principle of least privilege
   - Use IAM roles instead of access keys
   - Enable MFA for admin access

4. **Monitoring**
   - Enable audit logging
   - Set up alerts for unusual activity
   - Regular security scans

## Cost Optimization

### PostgreSQL
- Use reserved instances for production
- Right-size instance based on usage
- Implement read replicas only when needed

### Cloudflare
- Start with free tier
- Upgrade to paid tier only when needed
- Monitor R2 storage usage

### AWS
- Use spot instances for non-critical workloads
- Implement auto-scaling
- Set up billing alerts
- Review and optimize monthly

## Support

For issues or questions:
- Check documentation in `/docs`
- Review GitHub issues
- Contact: support@arbfinder.example.com

## Next Steps

After infrastructure is set up:
1. Deploy backend application
2. Deploy frontend application
3. Set up monitoring dashboards
4. Configure backup schedules
5. Run load tests
6. Document runbooks
