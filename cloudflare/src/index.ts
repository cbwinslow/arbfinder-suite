/**
 * Cloudflare Worker for ArbFinder Suite
 * Handles image uploads, data processing, and scheduled tasks
 */

export interface Env {
  IMAGES: R2Bucket;
  DATA: R2Bucket;
  BACKUPS: R2Bucket;
  CACHE: KVNamespace;
  SESSIONS: KVNamespace;
  ALERTS: KVNamespace;
  DB: D1Database;
  HYPERDRIVE?: Hyperdrive;
  ANALYTICS?: AnalyticsEngineDataset;
  SNIPE_QUEUE?: Queue;
  ALERT_QUEUE?: Queue;
  CRAWLER_QUEUE?: Queue;
  SNIPE_SCHEDULER: DurableObjectNamespace;
  API_BASE_URL: string;
  ENVIRONMENT: string;
  GOOGLE_TAG_MANAGER_ID?: string;
}

export default {
  /**
   * Main request handler
   */
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // Route handling
      if (url.pathname.startsWith('/api/upload/image')) {
        return await handleImageUpload(request, env, corsHeaders);
      } else if (url.pathname.startsWith('/api/images/')) {
        return await handleImageGet(request, env, corsHeaders);
      } else if (url.pathname === '/api/health') {
        return new Response(JSON.stringify({ status: 'ok', timestamp: Date.now() }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      return new Response('Not Found', { status: 404, headers: corsHeaders });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },

  /**
   * Scheduled task handler
   */
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    console.log('Scheduled task triggered:', event.cron);

    try {
      if (event.cron === '0 */4 * * *') {
        // Trigger crawler every 4 hours
        await triggerCrawler(env);
      } else if (event.cron === '*/15 * * * *') {
        // Process metadata queue every 15 minutes
        await processMetadataQueue(env);
      } else if (event.cron === '* * * * *') {
        // Check snipe schedules every minute
        await checkPendingSnipes(env);
        // Check alerts
        await checkPriceAlerts(env);
      }
    } catch (error) {
      console.error('Scheduled task error:', error);
    }
  },

  /**
   * Queue consumer handler
   */
  async queue(batch: MessageBatch<any>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      try {
        if (message.body.type === 'snipe') {
          await executeSnipe(message.body.data, env);
        } else if (message.body.type === 'alert') {
          await sendAlert(message.body.data, env);
        } else if (message.body.type === 'crawler') {
          await runCrawler(message.body.data, env);
        }
        message.ack();
      } catch (error) {
        console.error('Queue processing error:', error);
        message.retry();
      }
    }
  },
};

/**
 * Durable Object for snipe scheduling
 */
export class SnipeScheduler {
  private state: DurableObjectState;
  private env: Env;

  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
    this.env = env;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/schedule') {
      // Schedule a new snipe
      const snipeData = await request.json();
      const snipeId = `snipe-${Date.now()}`;
      
      // Store snipe data
      await this.state.storage.put(snipeId, snipeData);
      
      // Set alarm for execution
      const executeTime = snipeData.auction_end_time - snipeData.lead_time_seconds;
      await this.state.storage.setAlarm(executeTime * 1000);

      return new Response(JSON.stringify({ success: true, snipe_id: snipeId }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not found', { status: 404 });
  }

  async alarm(): Promise<void> {
    // Get all pending snipes
    const snipes = await this.state.storage.list();
    const now = Date.now() / 1000;

    for (const [snipeId, snipeData] of snipes) {
      const executeTime = snipeData.auction_end_time - snipeData.lead_time_seconds;
      
      if (now >= executeTime) {
        // Execute snipe via queue
        if (this.env.SNIPE_QUEUE) {
          await this.env.SNIPE_QUEUE.send({ type: 'snipe', data: snipeData });
        }
        
        // Remove from storage
        await this.state.storage.delete(snipeId);
      }
    }
  }
}

/**
 * Handle image upload to R2
 */
async function handleImageUpload(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405, headers: corsHeaders });
  }

  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return new Response(JSON.stringify({ error: 'No file provided' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Generate unique filename
    const filename = `${Date.now()}-${file.name}`;
    const buffer = await file.arrayBuffer();

    // Upload to R2
    await env.IMAGES.put(filename, buffer, {
      httpMetadata: {
        contentType: file.type,
      },
    });

    // Generate public URL
    const publicUrl = `https://images.arbfinder.com/${filename}`;

    return new Response(
      JSON.stringify({
        success: true,
        filename,
        url: publicUrl,
        size: buffer.byteLength,
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * Handle image retrieval from R2
 */
async function handleImageGet(
  request: Request,
  env: Env,
  corsHeaders: Record<string, string>
): Promise<Response> {
  const url = new URL(request.url);
  const filename = url.pathname.split('/').pop();

  if (!filename) {
    return new Response('Not found', { status: 404, headers: corsHeaders });
  }

  // Check cache first
  const cached = await env.CACHE.get(filename, 'arrayBuffer');
  if (cached) {
    return new Response(cached, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'image/*',
        'Cache-Control': 'public, max-age=31536000',
      },
    });
  }

  // Get from R2
  const object = await env.IMAGES.get(filename);
  if (!object) {
    return new Response('Not found', { status: 404, headers: corsHeaders });
  }

  const buffer = await object.arrayBuffer();

  // Cache for future requests
  await env.CACHE.put(filename, buffer, { expirationTtl: 86400 });

  return new Response(buffer, {
    headers: {
      ...corsHeaders,
      'Content-Type': object.httpMetadata?.contentType || 'image/*',
      'Cache-Control': 'public, max-age=31536000',
    },
  });
}

/**
 * Trigger crawler via API
 */
async function triggerCrawler(env: Env): Promise<void> {
  console.log('Triggering crawler...');
  
  try {
    const response = await fetch(`${env.API_BASE_URL}/api/crawler/run-all`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Crawler completed:', data);
    } else {
      console.error('Crawler failed:', response.status);
    }
  } catch (error) {
    console.error('Error triggering crawler:', error);
  }
}

/**
 * Process metadata enrichment queue
 */
async function processMetadataQueue(env: Env): Promise<void> {
  console.log('Processing metadata queue...');
  
  try {
    const response = await fetch(`${env.API_BASE_URL}/api/agents/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        agent_type: 'metadata_enricher',
        input_data: { batch_size: 50 },
      }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Metadata job created:', data);
    } else {
      console.error('Metadata job failed:', response.status);
    }
  } catch (error) {
    console.error('Error processing metadata queue:', error);
  }
}

/**
 * Check and execute pending snipes
 */
async function checkPendingSnipes(env: Env): Promise<void> {
  console.log('Checking pending snipes...');
  
  try {
    const response = await fetch(`${env.API_BASE_URL}/api/snipes/execute-pending`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Snipes executed:', data);
      
      // Track in analytics
      if (env.ANALYTICS && data.executed > 0) {
        env.ANALYTICS.writeDataPoint({
          blobs: ['snipe_executed'],
          doubles: [data.executed],
          indexes: ['system'],
        });
      }
    } else {
      console.error('Snipe execution failed:', response.status);
    }
  } catch (error) {
    console.error('Error checking pending snipes:', error);
  }
}

/**
 * Check price alerts
 */
async function checkPriceAlerts(env: Env): Promise<void> {
  console.log('Checking price alerts...');
  
  try {
    const response = await fetch(`${env.API_BASE_URL}/api/alerts/check-and-notify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Alerts checked:', data);
      
      // Track in analytics
      if (env.ANALYTICS && data.notifications_sent > 0) {
        env.ANALYTICS.writeDataPoint({
          blobs: ['alert_sent'],
          doubles: [data.notifications_sent],
          indexes: ['system'],
        });
      }
    } else {
      console.error('Alert check failed:', response.status);
    }
  } catch (error) {
    console.error('Error checking alerts:', error);
  }
}

/**
 * Execute a snipe (from queue)
 * TODO: PRODUCTION INTEGRATION REQUIRED
 * This function needs to be implemented to actually place bids on auction platforms
 * Required integrations: eBay API, ShopGoodwill API, etc.
 */
async function executeSnipe(snipeData: any, env: Env): Promise<void> {
  console.log('Executing snipe:', snipeData);
  // PLACEHOLDER: Call backend API which handles actual auction platform integration
  // Production: Direct auction platform API calls with proper authentication
}

/**
 * Send an alert notification (from queue)
 * TODO: PRODUCTION INTEGRATION REQUIRED
 * This function needs actual email/notification service integration
 * Required services: SendGrid, AWS SES, Mailgun, Twilio, etc.
 */
async function sendAlert(alertData: any, env: Env): Promise<void> {
  console.log('Sending alert:', alertData);
  // PLACEHOLDER: Call backend API which handles notification sending
  // Production: Direct calls to email/SMS/push notification services
}

/**
 * Run a crawler (from queue)
 * TODO: PRODUCTION INTEGRATION REQUIRED
 * This function needs to be implemented to run actual crawlers
 * Consider using Crawl4AI or similar frameworks
 */
async function runCrawler(crawlerData: any, env: Env): Promise<void> {
  console.log('Running crawler:', crawlerData);
  // PLACEHOLDER: Call backend API which handles crawler execution
  // Production: Run Crawl4AI/CrewAI agents directly or via queue
}
