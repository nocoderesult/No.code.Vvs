# fal.ai: generated inserts

`scripts/fal_run.py` calls fal.ai models for generated shots that cut into real footage, for example an AI macro
close-up at the moment a bottle opens.

## The key

- `FAL_KEY` lives in the git-ignored `.env` at the repository root (mode 600). `fal_run.py` reads it from the
  environment or from that file, and never prints, logs or passes it on a command line.
- If it is absent, follow fal's agent flow in https://fal.ai/get-started.md. POST `https://fal.ai/api/agent-connect`
  with the project name, then write the `verification_uri_complete` link and the `user_code` in your message. Poll
  the token endpoint in the background and append its 200 response to `.env`. The user only approves in the browser
  and never pastes a key. The key appears as "<project> (agent)" at https://fal.ai/dashboard/keys, where it can be
  revoked.
- A cloud session runs in a temporary container, so a key written there goes away with it. A new session repeats
  the approval.
- The agent key has the `API` preset. It can call models and read prices and storage settings, but not the balance:
  `/v1/account/billing` answers 403 "not permitted". The balance is on https://fal.ai/dashboard/usage-billing/credits.

## Cost and jobs

- `price` and `estimate` are free authenticated reads, and `schema` is public. Read the endpoint's
  `https://fal.ai/models/<endpoint-id>/llms.txt` before choosing parameters. The price per resolution tier is in its
  Pricing section, which `price` prints.
- `submit` is a dry run unless `--yes` is given. Each job's request id is appended to `<out>/fal_jobs.jsonl` before
  the wait. If the outcome is unclear, `resume` the job: a second submit is a second bill.
- On a 403, do not retry. With "Exhausted balance", the account needs credits (link above). Pass any other
  "User is locked" reason on to the user unchanged.
- Results are downloaded only from fal origins (`*.fal.media`, `*.fal.run`, `*.fal.ai`), into `fal_out/`
  (git-ignored).
- The Python SDK raises a bare `httpx.HTTPStatusError` when the storage token request fails, so its reason never
  shows. `fal_run.py` prints the response body.
