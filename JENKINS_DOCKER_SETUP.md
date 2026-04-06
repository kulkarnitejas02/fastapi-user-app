# Jenkins Docker Setup Guide

## Quick Start: Run Jenkins in Docker

### Option 1: Using Docker Compose (Recommended)

```bash
# Navigate to project directory
cd c:\Users\kulka\PycharmProjects\fastapi_user_app

# Start Jenkins
docker-compose up -d

# Watch logs (optional)
docker-compose logs -f jenkins
```

Jenkins will be available at: **http://localhost:8080**

### Option 2: Using Docker Run Command

```bash
docker run -d \
  --name fastapi-jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  --user 0:0 \
  jenkins/jenkins:latest
```

---

## First Time Setup

### 1. Get Initial Admin Password

```bash
# Using docker-compose
docker-compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# OR using docker run
docker exec fastapi-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 2. Access Jenkins

1. Open browser: **http://localhost:8080**
2. Paste the password from step 1
3. Click **Install suggested plugins** ✅
4. Create first admin user
5. Jenkins is ready!

---

## Install Required Plugins

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Available tab → Search for and install:
   - ✅ **Pipeline** (usually pre-installed)
   - ✅ **Git**
   - ✅ **Docker**
   - ✅ **Docker Pipeline** (optional)
   - ✅ **Blue Ocean** (optional - nice UI)

3. Restart Jenkins after installing plugins

---

## Configure Docker Hub Credentials

1. **Manage Jenkins** → **Manage Credentials**
2. Click **System** → **Global credentials** → **Add Credentials**
3. Fill in:
   - **Kind:** Username with password
   - **Username:** Your Docker Hub username
   - **Password:** Your Docker Hub access token (Settings → Security → Personal access tokens)
   - **ID:** `dockerhub-credentials` ⚠️ **Important: Must match Jenkinsfile**
   - **Description:** Docker Hub for FastAPI App
4. Click **Create**

---

## Update Jenkinsfile with Your Details

Edit [Jenkinsfile](Jenkinsfile#L5):

```groovy
DOCKER_IMAGE = 'your-actual-dockerhub-username/fastapi-app'
```

Example:
```groovy
DOCKER_IMAGE = 'johnsmith/fastapi-app'
```

---

## Create Pipeline Job

1. **Jenkins Dashboard** → **New Item**
2. **Name:** `fastapi-app-pipeline`
3. **Type:** Pipeline
4. **Pipeline section:**
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/your-username/fastapi_user_app.git`
   - Credentials: (select if private repo)
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
5. **Save**

---

## Run Your First Build

1. Click on pipeline job: **fastapi-app-pipeline**
2. Click **Build Now**
3. Watch the 5 stages execute in real-time:

```
✓ Checkout      → Clones code from GitHub
✓ Run Tests     → Runs 75 tests from tests/ dir
✓ Code Quality  → Linting with flake8
✓ Build Docker  → Creates image (excludes tests/)
✓ Push to Hub   → Pushes to Docker Hub (main branch only)
```

---

## Useful Docker Commands

```bash
# View logs
docker-compose logs -f jenkins

# Stop Jenkins
docker-compose down

# Start Jenkins again
docker-compose up -d

# SSH into Jenkins container (for debugging)
docker-compose exec jenkins bash

# Remove Jenkins entirely (data kept in volume)
docker-compose down

# Remove Jenkins + ALL DATA
docker-compose down -v
```

---

## What Happens in Each Stage

| Stage | Command | Success = | Failure = |
|-------|---------|-----------|-----------|
| **Checkout** | `git clone` | ✅ Proceed | ❌ Stop |
| **Tests** | `pytest tests/ -v` | ✅ Proceed | ❌ STOP - Don't build |
| **Quality** | `flake8` | ✅ Proceed | ⚠️ Continue (warning only) |
| **Docker Build** | `docker build -t ...` | ✅ Proceed | ❌ Stop |
| **Push to Hub** | `docker push ...` | ✅ Success | ❌ Fail (main branch only) |

---

## Port Mapping

- **8080** → Jenkins web UI
- **50000** → Jenkins agent communication
- Both mapped from container to localhost

---

## Docker Volume

Jenkins data is stored in `jenkins_home` Docker volume:
- Persists between container restarts
- Survives `docker-compose down`
- Contains: jobs, logs, credentials, plugins
- Location: `/var/lib/docker/volumes/jenkins_home/_data`

---

## Troubleshooting

### Jenkins won't start
```bash
# Check logs
docker-compose logs jenkins

# Try building from scratch
docker-compose down -v
docker-compose up -d
```

### Tests fail in Jenkins but pass locally
- Check Python version: `docker-compose exec jenkins python --version`
- Install requirements: Jenkins should auto-install from `requirements.txt`
- Check test output in console logs

### Docker build fails in Jenkins
- Jenkins needs access to Docker socket ✅ (configured in compose)
- Check disk space: `docker system df`
- Verify Dockerfile syntax: `docker build -t test:latest .`

### Docker push fails
- Verify Docker Hub credentials in Jenkins
- Check token is valid (not password)
- Verify credentials ID is `dockerhub-credentials`
- Check internet connection from Jenkins container

### Can't access Jenkins at localhost:8080
- Check if port 8080 is already in use: `netstat -an | findstr 8080`
- Check container is running: `docker ps | grep jenkins`
- Wait 30 seconds for Jenkins to fully start

---

## GitHub Webhook (Optional Auto-Trigger)

### Setup in GitHub:

1. Go to your repo → **Settings** → **Webhooks**
2. Click **Add webhook**
3. **Payload URL:** `http://your-server-ip:8080/github-webhook/`
4. **Content type:** `application/json`
5. **Events:** Push events
6. **Active:** ✅
7. Click **Add webhook**

Now every push to `main` automatically triggers the Jenkins pipeline!

---

## Monitor Builds

1. Go to **fastapi-app-pipeline**
2. Click build number to see details
3. Click **Console Output** to see real-time logs
4. Click **Test Result** to see test breakdown

---

## Next Steps

1. ✅ Start Jenkins with docker-compose
2. ✅ Complete initial setup (password, plugins)
3. ✅ Add Docker Hub credentials
4. ✅ Create pipeline job
5. ✅ Update Jenkinsfile with Docker Hub username
6. ✅ Push code to `main` branch
7. ✅ Click "Build Now"
8. ✅ Watch pipeline succeed end-to-end

Your pipeline will:
- ✅ Test all 75 test cases
- ✅ Build Docker image (no tests included)
- ✅ Push to Docker Hub
- ✅ All automated! 🚀
