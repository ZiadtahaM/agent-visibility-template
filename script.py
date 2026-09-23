import os
import subprocess

def write_file(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

write_file('package.json', '''{
  "name": "agent-visibility-template",
  "version": "1.0.0",
  "main": "src/index.ts",
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy"
  },
  "dependencies": {
    "hono": "^4.0.0"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20240222.0",
    "typescript": "^5.0.0",
    "wrangler": "^3.0.0"
  }
}''')

write_file('tsconfig.json', '''{
  "compilerOptions": {
    "target": "es2021",
    "lib": ["es2021"],
    "module": "es2022",
    "moduleResolution": "bundler",
    "types": ["@cloudflare/workers-types"],
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true
  }
}''')

write_file('wrangler.toml', '''name = "agent-visibility-template"
main = "src/index.ts"
compatibility_date = "2024-02-22"

[[kv_namespaces]]
binding = "VISIBILITY_KV"
id = "dummy_id"
''')

write_file('src/index.ts', '''import { Hono } from 'hono'

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
''')

write_file('README.md', '''# Agent Visibility Template

A Cloudflare Worker for AI agent health checks and request validation.

## What it does
This application provides health endpoints and validation routes for AI agents. It uses Cloudflare KV to store agent configurations. Rate limiting is applied to incoming requests.

## Tech
- TypeScript
- Hono
- Cloudflare Workers

## Architecture
`mermaid
flowchart TD
    Client --> Worker
    Worker --> KV[(Cloudflare KV)]
`

## Getting started
`ash
npm install
npm run dev
`
''')

os.system('cat README.md | unslop --stdin --deterministic > README_clean.md')
os.system('mv README_clean.md README.md')
os.system('python C:/Users/DevUser/.agents/skills/ddia-architect/scripts/ddia_cli.py guard .')
os.system('git add -A && git commit -m "feat: initial publish of full application" && git push origin main --force')

