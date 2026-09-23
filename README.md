# Agent Visibility Template

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
