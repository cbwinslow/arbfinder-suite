/**
 * Cloudflare Worker for ArbFinder Suite
 * Handles image uploads, data processing, and scheduled tasks
 */

export interface Env {
  IMAGES: R2Bucket;
  DATA: R2Bucket;
  CACHE: KVNamespace;
  API_BASE_URL: string;
  ENVIRONMENT: string;
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
      }
    } catch (error) {
      console.error('Scheduled task error:', error);
    }
  },
};

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
