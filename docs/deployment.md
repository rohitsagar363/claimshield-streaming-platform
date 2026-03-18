# ClaimShield Deployment

## Recommended Hosting

Deploy the dashboard to Streamlit Community Cloud.

Why:

- The app is a Streamlit server, not a stateless request-response function.
- It needs direct Kafka client access for live topic reads.
- It is the simplest free option for a shareable public demo URL.

Do not use Vercel for this Streamlit app in its current form.

## Prerequisites

- A GitHub repository containing this project
- Confluent Cloud resources already running
- A valid `OPENAI_API_KEY` if you want ClaimShield Copilot enabled

## Files Used By Deployment

- App entrypoint: `app/dashboard.py`
- Python dependencies: `requirements.txt`
- Secrets template: `.streamlit/secrets.example.toml`

## GitHub Steps

1. Create a new GitHub repository.
2. Push this project to the repository.
3. Keep the repository private if you do not want your code public.
4. If you deploy from a private repository, remember that Streamlit Community Cloud apps start private.

## Streamlit Community Cloud Steps

1. Sign in at Streamlit Community Cloud.
2. Click `New app`.
3. Select the GitHub repository for ClaimShield.
4. Set the main file path to `app/dashboard.py`.
5. Open the app advanced settings and add the required secrets.

## Required Secrets

Add these values in the Streamlit secrets editor:

```toml
KAFKA_BOOTSTRAP_SERVERS="pkc-56d1g.eastus.azure.confluent.cloud:9092"
KAFKA_API_KEY="..."
KAFKA_API_SECRET="..."

OPENAI_API_KEY="..."
CLAIMSHIELD_COPILOT_MODEL="gpt-5-mini"
```

Notes:

- `OPENAI_API_KEY` is optional if you want the dashboard without Copilot.
- `CLAIMSHIELD_COPILOT_MODEL` is optional and defaults to `gpt-5-mini`.

## Verification Checklist

After deployment, verify:

- The app loads without a dependency error.
- KPI cards render.
- The live alert feed shows records.
- The provider leaderboard shows records.
- ClaimShield Copilot can explain a selected alert.

## Demo Use

Use the public Streamlit URL in the submission form if you want reviewers to open the dashboard directly.

Also keep local screenshots ready in case Streamlit Community Cloud is slow during judging.
