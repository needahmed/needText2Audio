# Deployment Guide: Kokoro TTS Web App

This guide provides step-by-step instructions to deploy both the Python backend and the Next.js frontend of your application.

- **Backend (API Server)** will be deployed to **Heroku**.
- **Frontend (Web App)** will be deployed to **Vercel**.

This is the standard and most robust way to deploy a monorepo project like this.

## Prerequisites

1.  **Accounts**:

    - A [GitHub](https://github.com/) account (which you have).
    - A free [Heroku](https://signup.heroku.com/) account.
    - A free [Vercel](https://vercel.com/signup) account (you can sign up with your GitHub).

2.  **Tools**:
    - [Git](https://git-scm.com/downloads) installed on your machine.
    - The [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed on your machine.

---

## Part 1: Deploying the Python Backend to Heroku

Heroku will host our Python FastAPI server. Because our project is a monorepo, we need to tell Heroku to only look inside the `api-server` directory.

### Step 1: Login to Heroku

Open your terminal and run:

```bash
heroku login
```

This will open a browser window for you to log in.

### Step 2: Create a New Heroku Application

From the **root directory** of your project (`Kokoro-TTS`), run the following command. Make sure to choose a **unique name** for your app.

```bash
# Replace 'your-unique-app-name' with something unique
heroku create your-unique-app-name
```

This command also adds a new git remote named `heroku` to your local repository.

### Step 3: Push the `api-server` Subdirectory to Heroku

This is the most important step. We will use a `git subtree` command to push **only the contents of the `api-server` folder** to Heroku.

Run this command from the **root directory** of your project:

```bash
git subtree push --prefix api-server heroku main
```

This command tells Git to take the `api-server` folder and push it as the root of the `main` branch to your `heroku` remote.

Heroku will now detect the `requirements.txt`, `Procfile`, and `runtime.txt` files, install all the Python dependencies (including `torch` and `kokoro`), and start your server.

**Note:** This first deployment can take **5-10 minutes** because the TTS models are large.

### Step 4: Verify the Backend Deployment

Once the push is complete, you can open your app's URL to see if it's running.

```bash
heroku open
```

You should see `{"message":"Kokoro TTS API is running!"}`. You can also check the logs for any errors:

```bash
heroku logs --tail
```

> **IMPORTANT: Heroku Performance**
> The free "Eco Dyno" on Heroku has limited memory (512MB) and goes to sleep after inactivity. The Kokoro model is large and may cause the dyno to run slowly or time out, especially on the first request after it has gone to sleep. For more reliable performance, you may need to upgrade to a "Basic" or "Standard" dyno in the Heroku dashboard under the "Resources" tab.

---

## Part 2: Deploying the Next.js Frontend to Vercel

Vercel is the easiest way to deploy a Next.js application.

### Step 1: Push Your Latest Code to GitHub

Make sure all the recent changes (like the `deployment.md` file and the Heroku configurations) are on GitHub.

```bash
git add .
git commit -m "Configure for deployment"
git push origin main
```

### Step 2: Import Your Project into Vercel

1.  Log in to your [Vercel](https://vercel.com) dashboard.
2.  Click **Add New... -> Project**.
3.  Find your `needText2Audio` repository and click the **Import** button.

### Step 3: Configure the Vercel Project

This is a critical step to tell Vercel where your frontend code is.

1.  **Framework Preset**: Vercel should automatically detect **Next.js**.
2.  **Root Directory**: Expand the "Build and Output Settings" section and set the **Root Directory** to `web-app`.

    ![Vercel Root Directory Setting](https://i.imgur.com/your-image-url.png) <!-- It would be great to have an actual image here, but this text will have to do. -->

3.  **Environment Variables**: Go to the "Environment Variables" section. Add the following:
    - **Name**: `NEXT_PUBLIC_API_URL`
    - **Value**: The URL of your live Heroku app (e.g., `https://your-unique-app-name.herokuapp.com`). You can get this from your Heroku dashboard or by running `heroku apps:info`.

### Step 4: Deploy

Click the **Deploy** button. Vercel will build and deploy your frontend. This process is usually very fast.

---

## Part 3: Final Connection

There is one final step to ensure your frontend and backend can communicate securely.

1.  **Get Your Vercel URL**: Once your Vercel deployment is complete, it will have a URL like `https://needtext2audio-xyz.vercel.app`. Copy this URL.

2.  **Set the `FRONTEND_URL` on Heroku**:
    - Go to your Heroku App's dashboard.
    - Click on the **Settings** tab.
    - Click **Reveal Config Vars**.
    - Add a new Config Var:
      - **KEY**: `FRONTEND_URL`
      - **VALUE**: Paste your Vercel URL here (e.g., `https://needtext2audio-xyz.vercel.app`).

Heroku will automatically restart your app with this new environment variable. Your frontend is now officially in the list of allowed origins for your backend API.

**Congratulations! Your application is now fully deployed and live on the internet.**
