# Credit pe contul fal

Type: task
Status: resolved
Blocked by: —

## Question

Contul fal are credit, ca upload-ul și generările să meargă? Primul upload în stocarea fal a primit 403, fără motiv
vizibil. Tu adaugi credit pe https://fal.ai/dashboard/usage-billing/credits, apoi refac upload-ul cu un cadru de test
și notez rezultatul (sau motivul exact al refuzului).

## Answer

Tu ai pus credit pe cont. Upload-ul de test (un cadru sintetic, fără cost) a mers și pe 10 noiembrie a fost salvat pe
`v3b.fal.media`, iar fișierul se citește înapoi (HTTP 200). Primul 403 a fost înainte de credit.
