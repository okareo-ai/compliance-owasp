# Quickstart: Target Agent Auth Flow Configuration

**Branch**: `011-target-auth-flow` | **Date**: 2026-03-12

## Overview

The shared target configuration (`owasp/target.env`) now supports the full Okareo flow: **Auth → Start → Next → End**. Only **Next** is required. Auth, Start, and End are optional. This allows OWASP evaluations to run against agents that require authentication (e.g., OAuth2 token acquisition) before accepting requests.

## Prerequisites

- Python 3.11+
- Okareo API key (in `.env`)
- A deployed agent accessible via HTTP
- (If Auth required) An auth/token endpoint (e.g., OAuth2) and credentials

## Setup for Stateless Agents (No Auth, No Session)

1. Copy the template and set the Next endpoint:

```bash
cp owasp/target.env.example owasp/target.env
# Edit owasp/target.env:
#   TARGET_NAME=my-agent
#   TARGET_ENDPOINT_URL=https://your-agent.example.com/chat
#   TARGET_REQUEST_BODY={"message": "{latest_message}"}
#   TARGET_RESPONSE_PATH=response
```

2. Run any OWASP category notebook. The target loads automatically; no code changes.

## Setup for Auth-Protected Agents

1. Copy the template:

```bash
cp owasp/target.env.example owasp/target.env
```

2. Configure the Next endpoint and Auth step in `owasp/target.env`:

```env
TARGET_NAME=my-agent
TARGET_ENDPOINT_URL=https://your-agent.example.com/chat
TARGET_REQUEST_BODY={"message": "{latest_message}", "Authorization": "Bearer {access_token}"}
TARGET_RESPONSE_PATH=response

# Auth step — acquire token before each conversation
TARGET_AUTH_URL=https://auth.example.com/oauth2/token
TARGET_AUTH_METHOD=POST
TARGET_AUTH_HEADERS=Content-Type: application/x-www-form-urlencoded
TARGET_AUTH_BODY=grant_type=client_credentials&client_id=$TARGET_AUTH_CLIENT_ID&client_secret=$TARGET_AUTH_CLIENT_SECRET
TARGET_AUTH_RESPONSE_TOKEN_PATH=response.access_token
```

3. Set Auth credentials in `.env` (never commit):

```env
OKAREO_API_KEY=your_okareo_key
TARGET_AUTH_CLIENT_ID=your_client_id
TARGET_AUTH_CLIENT_SECRET=your_client_secret
```

4. Run any OWASP category notebook. The target is registered with Auth, and evaluations acquire a token before the first turn.

## Setup for Session-Based Agents (Start + End)

If your agent requires explicit session creation and teardown:

```env
TARGET_NAME=my-agent
TARGET_ENDPOINT_URL=https://your-agent.example.com/chat
TARGET_REQUEST_BODY={"message": "{latest_message}", "session_id": "{session_id}"}
TARGET_RESPONSE_PATH=response

TARGET_SESSION_START_URL=https://your-agent.example.com/session/start
TARGET_SESSION_ID_PATH=response.session_id

TARGET_SESSION_END_URL=https://your-agent.example.com/session/end
TARGET_SESSION_END_BODY={"session_id": "{session_id}"}
```

## Setup for Full Flow (Auth + Start + Next + End)

Combine Auth, Start, Next, and End when your agent requires all four:

```env
TARGET_NAME=my-agent
TARGET_ENDPOINT_URL=https://your-agent.example.com/chat
TARGET_REQUEST_BODY={"message": "{latest_message}", "session_id": "{session_id}", "Authorization": "Bearer {access_token}"}
TARGET_RESPONSE_PATH=response

TARGET_AUTH_URL=https://auth.example.com/oauth2/token
TARGET_AUTH_BODY=grant_type=client_credentials&client_id=$TARGET_AUTH_CLIENT_ID&client_secret=$TARGET_AUTH_CLIENT_SECRET
TARGET_AUTH_RESPONSE_TOKEN_PATH=response.access_token

TARGET_SESSION_START_URL=https://your-agent.example.com/session/start
TARGET_SESSION_START_BODY={"Authorization": "Bearer {access_token}"}
TARGET_SESSION_ID_PATH=response.session_id

TARGET_SESSION_END_URL=https://your-agent.example.com/session/end
TARGET_SESSION_END_BODY={"session_id": "{session_id}", "Authorization": "Bearer {access_token}"}
```

## Template Variables

| Variable | Available In | Description |
|----------|--------------|-------------|
| `{latest_message}` | Next body | The user's message for the current turn |
| `{session_id}` | Next, End body | Session ID from Start response |
| `{access_token}` | Start, Next, End body/headers | Token from Auth response (when Auth configured) |

## Troubleshooting

- **"TARGET_ENDPOINT_URL not set"**: Ensure `owasp/target.env` exists and contains `TARGET_ENDPOINT_URL`.
- **"Could not extract token"**: Check `TARGET_AUTH_RESPONSE_TOKEN_PATH` matches your auth response structure (e.g., `response.access_token` for `{"access_token": "..."}`).
- **401 on downstream calls**: Ensure `{access_token}` is included in headers or body of Start/Next/End (e.g., `Authorization: Bearer {access_token}`).
- **Empty client_secret**: Set `TARGET_AUTH_CLIENT_SECRET` in `.env`; `$TARGET_AUTH_CLIENT_SECRET` in `TARGET_AUTH_BODY` is substituted at load time.
