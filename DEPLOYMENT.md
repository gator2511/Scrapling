# Deploy Scrapling as a remote MCP server

This repository includes a Render Blueprint for running Scrapling as an authenticated Streamable HTTP MCP server.

## Deploy

1. Sign in to Render and create a new **Blueprint**.
2. Select this GitHub repository: `gator2511/Scrapling`.
3. Render reads `render.yaml` and creates the `scrapling-mcp` Docker web service.
4. Approve the deployment.

The service starts with:

```text
scrapling mcp --http --host 0.0.0.0 --port 8000
```

Render generates a secret `SCRAPLING_MCP_AUTH_TOKEN` automatically. Retrieve it from the service's **Environment** page and keep it private.

## Connect

The MCP endpoint is normally:

```text
https://<your-render-hostname>/mcp
```

Configure the MCP client to use Streamable HTTP and send:

```text
Authorization: Bearer <SCRAPLING_MCP_AUTH_TOKEN>
```

## Capacity warning

The Blueprint uses Render's free plan to avoid creating a paid service without approval. Chromium-based `fetch`, `stealthy_fetch`, bulk operations, and concurrent sessions can exceed free-tier memory or startup limits. Upgrade the instance before using browser-heavy or production workloads.

## Security and responsible use

Do not remove authentication before exposing the server publicly. Only scrape sites you are authorised to access, and comply with applicable privacy laws, website terms, rate limits, and `robots.txt` rules.
