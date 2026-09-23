import { Hono } from 'hono'

type Bindings = {
  VISIBILITY_KV: KVNamespace
}

const app = new Hono<{ Bindings: Bindings }>()

const RATE_LIMIT_WINDOW = 60000;
const MAX_REQUESTS = 100;
const ipRequests = new Map<string, { count: number, resetAt: number }>();

app.use('*', async (c, next) => {
  const ip = c.req.header('cf-connecting-ip') || 'unknown';
  const now = Date.now();
  
  const record = ipRequests.get(ip);
  if (record) {
    if (now > record.resetAt) {
      ipRequests.set(ip, { count: 1, resetAt: now + RATE_LIMIT_WINDOW });
    } else {
      if (record.count >= MAX_REQUESTS) {
        return c.text('Too Many Requests', 429);
      }
      record.count += 1;
    }
  } else {
    ipRequests.set(ip, { count: 1, resetAt: now + RATE_LIMIT_WINDOW });
  }
  
  await next();
});

app.get('/health', (c) => {
  return c.json({ status: 'ok', component: 'ai-agent-health-check' })
})

app.post('/validate', async (c) => {
  const body = await c.req.json().catch(() => null)
  if (!body || !body.agentId) {
    return c.json({ error: 'Missing agentId' }, 400)
  }
  await c.env.VISIBILITY_KV.put('agent:' + body.agentId, JSON.stringify(body))
  return c.json({ success: true })
})

export default app
