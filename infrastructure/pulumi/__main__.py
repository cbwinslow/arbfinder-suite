"""
Pulumi Infrastructure as Code for ArbFinder Suite
Deploys PostgreSQL database, Cloudflare Workers, and backend services
"""

import pulumi
import pulumi_postgresql as postgresql
import pulumi_cloudflare as cloudflare
import pulumi_aws as aws
import json
from pulumi import Config, Output, export

# Load configuration
config = Config()
environment = config.get("environment") or "development"
domain = config.get("domain") or "arbfinder.example.com"

# Tags for all resources
tags = {
    "Project": "ArbFinder Suite",
    "Environment": environment,
    "ManagedBy": "Pulumi"
}

# ============================================================================
# PostgreSQL Database Setup
# ============================================================================

# PostgreSQL provider configuration
pg_config = Config("postgresql")
pg_host = pg_config.require("host")
pg_port = pg_config.get_int("port") or 5432
pg_username = pg_config.require("username")
pg_password = pg_config.require_secret("password")
pg_database = pg_config.get("database") or "arbfinder"

# Database provider
pg_provider = postgresql.Provider(
    "pg-provider",
    host=pg_host,
    port=pg_port,
    username=pg_username,
    password=pg_password,
    superuser=False
)

# Create database if not exists (requires superuser)
database = postgresql.Database(
    "arbfinder-db",
    name=pg_database,
    opts=pulumi.ResourceOptions(provider=pg_provider)
)

# Create application user
app_user = postgresql.Role(
    "arbfinder-app-user",
    name="arbfinder_app",
    login=True,
    password=config.require_secret("db_app_password"),
    opts=pulumi.ResourceOptions(provider=pg_provider)
)

# Create read-only user for analytics
readonly_user = postgresql.Role(
    "arbfinder-readonly-user",
    name="arbfinder_readonly",
    login=True,
    password=config.require_secret("db_readonly_password"),
    opts=pulumi.ResourceOptions(provider=pg_provider)
)

# Grant permissions to app user
app_grants = postgresql.Grant(
    "arbfinder-app-grants",
    database=database.name,
    role=app_user.name,
    object_type="database",
    privileges=["CREATE", "CONNECT", "TEMPORARY"],
    opts=pulumi.ResourceOptions(
        provider=pg_provider,
        depends_on=[database, app_user]
    )
)

# Grant read-only access
readonly_grants = postgresql.Grant(
    "arbfinder-readonly-grants",
    database=database.name,
    role=readonly_user.name,
    object_type="database",
    privileges=["CONNECT"],
    opts=pulumi.ResourceOptions(
        provider=pg_provider,
        depends_on=[database, readonly_user]
    )
)

# ============================================================================
# Cloudflare Setup
# ============================================================================

cf_config = Config("cloudflare")
cf_zone_id = cf_config.require("zone_id")
cf_account_id = cf_config.require("account_id")

# Cloudflare D1 Database for edge caching
d1_database = cloudflare.D1Database(
    "arbfinder-d1-cache",
    account_id=cf_account_id,
    name=f"arbfinder-cache-{environment}"
)

# Cloudflare R2 Bucket for images and metadata
r2_bucket = cloudflare.R2Bucket(
    "arbfinder-r2-storage",
    account_id=cf_account_id,
    name=f"arbfinder-storage-{environment}",
    location="auto"
)

# Cloudflare Worker for data ingestion
worker_script = """
// ArbFinder Data Ingestion Worker
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  }
  
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }
  
  try {
    // Route handling
    if (url.pathname === '/api/ingest') {
      return await handleIngest(request, corsHeaders)
    } else if (url.pathname === '/api/items') {
      return await handleItems(request, corsHeaders)
    } else if (url.pathname === '/api/health') {
      return new Response(JSON.stringify({ status: 'healthy' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
    
    return new Response('Not Found', { status: 404 })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

async function handleIngest(request, corsHeaders) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }
  
  const data = await request.json()
  
  // Validate required fields
  if (!data.title || !data.price || !data.source) {
    return new Response(JSON.stringify({ 
      error: 'Missing required fields: title, price, source' 
    }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
  
  // Store in D1 cache
  const itemId = crypto.randomUUID()
  await CACHE_DB.prepare(
    'INSERT INTO items_cache (id, data, created_at) VALUES (?, ?, ?)'
  ).bind(itemId, JSON.stringify(data), Date.now()).run()
  
  // Queue for PostgreSQL ingestion
  await INGESTION_QUEUE.send({
    id: itemId,
    data: data,
    timestamp: Date.now()
  })
  
  return new Response(JSON.stringify({ 
    success: true, 
    id: itemId 
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
}

async function handleItems(request, corsHeaders) {
  if (request.method !== 'GET') {
    return new Response('Method not allowed', { status: 405 })
  }
  
  // Get items from cache
  const result = await CACHE_DB.prepare(
    'SELECT * FROM items_cache ORDER BY created_at DESC LIMIT 100'
  ).all()
  
  return new Response(JSON.stringify({ 
    items: result.results 
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
}
"""

worker = cloudflare.WorkerScript(
    "arbfinder-ingestion-worker",
    account_id=cf_account_id,
    name=f"arbfinder-ingestion-{environment}",
    content=worker_script,
    d1_database_bindings=[
        cloudflare.WorkerScriptD1DatabaseBindingArgs(
            name="CACHE_DB",
            database_id=d1_database.id
        )
    ]
)

# Worker route
worker_route = cloudflare.WorkerRoute(
    "arbfinder-worker-route",
    zone_id=cf_zone_id,
    pattern=f"api.{domain}/ingest/*",
    script_name=worker.name
)

# Cloudflare DNS record
dns_record = cloudflare.Record(
    "arbfinder-api-dns",
    zone_id=cf_zone_id,
    name=f"api.{domain}",
    type="CNAME",
    value=f"arbfinder-ingestion-{environment}.workers.dev",
    proxied=True
)

# ============================================================================
# AWS Resources (Optional - for backend services)
# ============================================================================

aws_config = Config("aws")
if aws_config.get("enabled") == "true":
    # VPC for backend services
    vpc = aws.ec2.Vpc(
        "arbfinder-vpc",
        cidr_block="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={**tags, "Name": "arbfinder-vpc"}
    )
    
    # Internet Gateway
    igw = aws.ec2.InternetGateway(
        "arbfinder-igw",
        vpc_id=vpc.id,
        tags={**tags, "Name": "arbfinder-igw"}
    )
    
    # Public Subnets
    public_subnet_1 = aws.ec2.Subnet(
        "arbfinder-public-subnet-1",
        vpc_id=vpc.id,
        cidr_block="10.0.1.0/24",
        availability_zone="us-east-1a",
        map_public_ip_on_launch=True,
        tags={**tags, "Name": "arbfinder-public-1"}
    )
    
    public_subnet_2 = aws.ec2.Subnet(
        "arbfinder-public-subnet-2",
        vpc_id=vpc.id,
        cidr_block="10.0.2.0/24",
        availability_zone="us-east-1b",
        map_public_ip_on_launch=True,
        tags={**tags, "Name": "arbfinder-public-2"}
    )
    
    # Security Group for API
    api_security_group = aws.ec2.SecurityGroup(
        "arbfinder-api-sg",
        vpc_id=vpc.id,
        description="Security group for ArbFinder API",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=80,
                to_port=80,
                cidr_blocks=["0.0.0.0/0"]
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["0.0.0.0/0"]
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=8080,
                to_port=8080,
                cidr_blocks=["0.0.0.0/0"]
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"]
            )
        ],
        tags={**tags, "Name": "arbfinder-api-sg"}
    )
    
    # ECS Cluster for backend services
    ecs_cluster = aws.ecs.Cluster(
        "arbfinder-ecs-cluster",
        name=f"arbfinder-{environment}",
        tags=tags
    )
    
    # ECR Repository for Docker images
    ecr_repo = aws.ecr.Repository(
        "arbfinder-ecr-repo",
        name=f"arbfinder-suite-{environment}",
        image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
            scan_on_push=True
        ),
        tags=tags
    )
    
    # S3 Bucket for backups
    backup_bucket = aws.s3.Bucket(
        "arbfinder-backups",
        bucket=f"arbfinder-backups-{environment}",
        versioning=aws.s3.BucketVersioningArgs(
            enabled=True
        ),
        lifecycle_rules=[
            aws.s3.BucketLifecycleRuleArgs(
                enabled=True,
                transitions=[
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=30,
                        storage_class="STANDARD_IA"
                    ),
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=90,
                        storage_class="GLACIER"
                    )
                ]
            )
        ],
        tags=tags
    )
    
    # Export AWS resources
    export("vpc_id", vpc.id)
    export("ecs_cluster_name", ecs_cluster.name)
    export("ecr_repository_url", ecr_repo.repository_url)
    export("backup_bucket_name", backup_bucket.bucket)

# ============================================================================
# Secrets Manager
# ============================================================================

# Store database connection string in AWS Secrets Manager
if aws_config.get("enabled") == "true":
    db_connection_secret = aws.secretsmanager.Secret(
        "arbfinder-db-connection",
        name=f"arbfinder/db-connection-{environment}",
        tags=tags
    )
    
    db_connection_string = Output.all(
        pg_host, pg_port, pg_database, pg_username, pg_password
    ).apply(
        lambda args: f"postgresql://{args[3]}:{args[4]}@{args[0]}:{args[1]}/{args[2]}"
    )
    
    db_connection_secret_version = aws.secretsmanager.SecretVersion(
        "arbfinder-db-connection-version",
        secret_id=db_connection_secret.id,
        secret_string=db_connection_string
    )
    
    export("db_secret_arn", db_connection_secret.arn)

# ============================================================================
# Monitoring and Logging
# ============================================================================

if aws_config.get("enabled") == "true":
    # CloudWatch Log Group
    log_group = aws.cloudwatch.LogGroup(
        "arbfinder-logs",
        name=f"/arbfinder/{environment}",
        retention_in_days=30,
        tags=tags
    )
    
    # SNS Topic for alerts
    alert_topic = aws.sns.Topic(
        "arbfinder-alerts",
        name=f"arbfinder-alerts-{environment}",
        tags=tags
    )
    
    # CloudWatch Alarms
    high_error_rate_alarm = aws.cloudwatch.MetricAlarm(
        "arbfinder-high-error-rate",
        comparison_operator="GreaterThanThreshold",
        evaluation_periods=2,
        metric_name="Errors",
        namespace="AWS/Lambda",
        period=300,
        statistic="Sum",
        threshold=10,
        alarm_description="Alert when error rate is high",
        alarm_actions=[alert_topic.arn],
        tags=tags
    )
    
    export("log_group_name", log_group.name)
    export("alert_topic_arn", alert_topic.arn)

# ============================================================================
# Exports
# ============================================================================

# Database exports
export("database_name", database.name)
export("database_host", pg_host)
export("database_port", pg_port)
export("app_user_name", app_user.name)
export("readonly_user_name", readonly_user.name)

# Cloudflare exports
export("d1_database_id", d1_database.id)
export("r2_bucket_name", r2_bucket.name)
export("worker_script_name", worker.name)
export("api_domain", f"api.{domain}")

# Connection strings (masked)
export("app_connection_string", Output.secret(
    Output.all(pg_host, pg_port, pg_database, app_user.name).apply(
        lambda args: f"postgresql://{args[3]}:***@{args[0]}:{args[1]}/{args[2]}"
    )
))

print(f"✅ ArbFinder Suite infrastructure deployed for {environment} environment")
