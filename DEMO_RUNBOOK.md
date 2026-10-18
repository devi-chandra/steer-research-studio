# Steer Lens demo runbook

Use this runbook for a repeatable local demo. The sample paper is a pipeline fixture; verify the publication and source details before presenting any health content as real research.

## Clean start

1. Open PowerShell in the project root.
2. Start the backend in terminal one:

   ```powershell
   cd backend
   pip install -r requirements.txt
   $env:PYTHONPATH = "."
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

3. Start the frontend in terminal two:

   ```powershell
   cd frontend
   npm ci
   npm run dev -- --host 127.0.0.1 --port 5173
   ```

4. Open `http://127.0.0.1:5173/`, use the sample-paper demo, and render the carousel, static post, and reel.
5. In Export Center, run **Run rendered asset checks**. Resolve missing files or format flags, then inspect every slide and subtitle manually. The automated check does not assess text clipping, legibility, visual polish, or whether a health statement is accurate.
6. Run **Ask a question this paper may not answer**. The fixture question asks whether tapering semaglutide prevents regain. The included walking paper should return a refusal because its claims do not answer that question. This is a routing demonstration, not clinical advice.
7. Open Medical Review. Show the source quote and page, the overclaim warnings, and the fact that approval applies to a numbered content version. Do not describe a simulated reviewer as a doctor.
8. Build provisional exports for the walkthrough. Label them as drafts unless the exact content version and its claims received genuine clinical approval.

## Submission freeze checklist

- [ ] Keep the submission run on a clean checkout with `npm ci` and `pip install -r backend/requirements.txt`.
- [ ] Run `npm run build` from `frontend` before recording.
- [ ] Run the backend suite using the command in the main README and resolve failures before describing the suite as passing.
- [ ] Process 2–3 real, cited papers and check each paper’s source, design, population, findings, and limitations.
- [ ] Package one final carousel, one static post, one reel, each caption and its reasoning, plus the source claim ledger.
- [ ] Inspect final media at phone size. Automated file checks are only a first pass.
- [ ] Record the Loom from the same frozen demo state and disclose tools, prompts, contributors, and any simulated review.

## Reproducible unsupported-source check

After processing the sample walking paper, open Export Center and click **Ask a question this paper may not answer**. The app sends this fixed question to the project’s evidence-fit endpoint:

> Does tapering semaglutide prevent weight regain?

The response includes the matched topic terms, overlap score, answerability label, and a refusal message when the source does not support the topic. This lexical check is deliberately presented as a routing hint; it cannot establish that a paper answers a clinical question.
