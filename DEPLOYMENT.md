# Deploy Steer (Vercel + Railway)

This setup deploys the Vite frontend to Vercel and the FastAPI backend to Railway. Railway's free allowance is limited, so check its current plan limits before relying on it for a permanent public service.

## 1. Deploy the backend to Railway

1. Create a Railway project from the GitHub repository and select the `sush-2` branch.
2. In the service settings, set the root directory to `/backend`. Railway will build `backend/Dockerfile`.
3. Add a Railway Volume and mount it at `/data`.
4. Add these variables in the service's Variables panel:

   ```text
   DEBUG=false
   HOST=0.0.0.0
   CORS_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
   STORAGE_DIR=/data
   UPLOADS_DIR=/data/uploads
   GENERATED_DIR=/data/generated
   EXPORTS_DIR=/data/exports
   DATABASE_PATH=/data/steer_studio.db
   FFMPEG_PATH=ffmpeg
   AI_PROVIDER=deterministic
   TTS_PROVIDER=edge-tts
   ```

   Railway injects `PORT`; the Docker command binds Uvicorn to it. The app stores the SQLite database, uploads and generated files under the mounted volume.
5. Generate a public domain for the backend and verify `https://<backend-domain>/api/health` returns a healthy response.

Optional AI provider secrets (`GEMINI_API_KEY`, `OPENAI_API_KEY`) should only be set in Railway's Variables panel, never in frontend variables or committed files.

## 2. Deploy the frontend to Vercel

1. Import the same repository into Vercel and select the `sush-2` branch.
2. Set the Root Directory to `frontend`.
3. Use the Vite defaults: build command `npm run build`, output directory `dist`, install command `npm install`.
4. Add this environment variable for Production:

   ```text
   VITE_API_BASE_URL=https://<backend-domain>
   ```

5. Deploy, then copy the Vercel production URL (for example `https://<project>.vercel.app`).

## 3. Lock backend CORS to the deployed frontend

Back in Railway, replace `CORS_ORIGINS` with the exact Vercel production origin, without a trailing slash:

```text
CORS_ORIGINS=https://<project>.vercel.app
```

If using a custom domain, list both origins separated by a comma. Redeploy/restart the Railway service after changing the variable. Then test PDF upload, evidence extraction, content generation, review, exports, and reel rendering. Keep in mind the Railway volume is small on the free/trial tier and generated media can consume it quickly.
