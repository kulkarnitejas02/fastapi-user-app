# Jenkins CI/CD Pipeline Setup Guide

## Pipeline Overview

The Jenkins pipeline automates the complete software lifecycle:

```
Code Push → Checkout → Tests → Code Quality → Docker Build → Push to Hub
```

## Pipeline Stages

### 1️⃣ **Checkout** 
- Clones the latest code from your Git repository
- Status: Always runs
- Duration: ~30 seconds

### 2️⃣ **Run Comprehensive Tests** ⭐ CRITICAL
- Runs all 75 test cases from `tests/` directory
- Tests include:
  - Schema validation (28 tests)
  - Security vulnerabilities (19 tests)
  - Edge cases (19 tests)
  - Core API functionality (14 tests)
- **Pipeline stops here if any test fails** ❌
- Status: Must pass to proceed
- Duration: ~3-5 seconds

### 3️⃣ **Code Quality Check**
- Runs flake8 linting
- Checks Python code style and standards
- Non-blocking (won't stop pipeline if fails)
- Status: Warning only
- Duration: ~5 seconds

### 4️⃣ **Build Docker Image** 🐳
- Creates Docker image excluding:
  - `tests/` directory
  - `.git/` directory
  - `.gitignore`, `README.md`, `TESTING_REPORT.md`
- Tags image as `your-dockerhub-username/fastapi-app:BUILD_NUMBER`
- Also tags as `latest`
- Status: Must succeed to proceed
- Duration: ~30-60 seconds

### 5️⃣ **Push to Docker Hub** 📤
- Only runs on `main` branch (safety feature)
- Logs in with Docker Hub credentials
- Pushes tagged image and latest tag
- Cleans up credentials after push
- Status: Final stage
- Duration: ~20-40 seconds (depending on image size)

---

## Prerequisites Setup

### 1. Create Docker Hub Credentials in Jenkins

1. Go to **Jenkins Dashboard** → **Manage Jenkins** → **Manage Credentials**
2. Click **System** → **Global credentials**
3. Click **Add Credentials**
4. Fill in:
   - **Kind**: Username with password
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub access token (NOT password)
   - **ID**: `dockerhub-credentials` (must match Jenkinsfile)
   - **Description**: Docker Hub Credentials for FastAPI App
5. Click **Create**

### 2. Configure Git Repository

1. Go to **Jenkins Dashboard** → **New Item**
2. Enter name: `fastapi-app-pipeline`
3. Choose **Pipeline**
4. Click **OK**
5. In **Pipeline** section, choose **Pipeline script from SCM**
6. Select **Git**
7. Fill in:
   - **Repository URL**: `https://github.com/your-username/fastapi_user_app.git`
   - **Credentials**: Add if private repo
   - **Branch**: `*/main` (or your branch)
8. In **Script Path**: `Jenkinsfile`
9. Click **Save**

### 3. Update Jenkinsfile Variable

Replace `your-dockerhub-username` with your actual Docker Hub username:

```groovy
DOCKER_IMAGE = 'your-actual-username/fastapi-app'
```

### 4. Update Git Configuration (Optional)

If using webhook for auto-trigger:
1. Go to GitHub repository → **Settings** → **Webhooks**
2. Add webhook:
   - **Payload URL**: `http://your-jenkins-server/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Push events
   - **Active**: ✅

---

## Running the Pipeline

### Manual Trigger
1. Go to Jenkins Dashboard
2. Click **fastapi-app-pipeline**
3. Click **Build Now**
4. Watch the build progress in real-time

### Automatic Trigger (with webhook)
1. Push code to `main` branch
2. GitHub webhook automatically triggers Jenkins
3. Pipeline runs automatically

---

## Pipeline Execution Flow

```
┌─────────────────────────────────────────┐
│          Code Push to Git               │
└─────────────────┬───────────────────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │   Checkout Stage    │
        └──────────┬──────────┘
                   │
                   ▼
     ┌──────────────────────────────┐
     │  Run Tests from tests/  ⭐   │
     │  - 75 test cases             │
     │  - Must all pass!            │
     └────────────┬─────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
      PASS              FAIL ❌
        │                   │
        ▼                   ▼
   Continue          PIPELINE STOPS
        │           Build fails
        ▼           Notify user
   Code Quality
   Check
        │
        ▼
   Build Docker
   Image 🐳
        │
   ┌────┴────┐
   │          │
 PASS     FAIL ❌
   │      Build fails
   ▼      Notify user
 Push to
 Docker Hub
 (main branch only)
   │
   ▼
PIPELINE SUCCESS ✓
```

---

## Monitoring & Logs

### View Build Logs
1. Click on build number
2. Click **Console Output**
3. View real-time logs

### View Test Results
- Click on build
- Click **Test Result** 
- See detailed test breakdown

### View Docker Images Built
- Each build creates:
  - `fastapi-app:BUILD_NUMBER` (e.g., `fastapi-app:42`)
  - `fastapi-app:latest` (always points to latest build)

---

## Troubleshooting

### Tests Fail
- Check **Console Output** for test errors
- Fix issues locally and run `pytest tests/ -v`
- Commit and push fixed code
- Pipeline will retry automatically (if webhook configured)

### Docker Build Fails
- Ensure Docker is installed on Jenkins agent
- Check Dockerfile syntax: `docker build -t test:latest .`
- Verify all dependencies in `requirements.txt`

### Docker Push Fails
- Verify Docker Hub credentials in Jenkins
- Check username/password in Manage Credentials
- Ensure Docker Hub repository exists
- Check internet connectivity

### Pipeline Stuck on "Push to Docker Hub"
- Only runs on `main` branch
- Ensure branch is `main` or update Jenkinsfile condition
- Or manually merge to main branch

---

## Pipeline Statistics

| Metric | Value |
|--------|-------|
| **Total Stages** | 5 |
| **Critical Stages** | 2 (Tests, Docker Build) |
| **Test Cases Run** | 75 |
| **Average Runtime** | ~2-3 minutes |
| **Success Rate Target** | 100% |
| **Failure Tolerance** | 0 (all tests must pass) |

---

## Environment Variables Available

Inside pipeline script, you can use:

```groovy
env.BUILD_NUMBER      // Build number (1, 2, 3...)
env.WORKSPACE         // Jenkins workspace path
env.BRANCH_NAME       // Git branch name
env.GIT_COMMIT        // Commit hash
env.JOB_NAME          // Job name
```

---

## Security Best Practices

✅ **Implemented:**
- Docker Hub credentials stored securely in Jenkins
- Credentials not exposed in logs
- Docker logout after push
- Tests verify authentication
- Tests check for SQL injection
- Tests validate input sanitization

⚠️ **Recommended:**
- Use GitHub branch protection rules
- Require status checks to pass before merge
- Enable pipeline signing
- Monitor build history for anomalies
- Regularly rotate Docker Hub access tokens

---

## Next Steps

1. ✅ Add credentials to Jenkins
2. ✅ Create Pipeline job
3. ✅ Configure Git repository
4. ✅ Update Docker Hub username in Jenkinsfile
5. ✅ Test manual trigger
6. ✅ Set up GitHub webhook for auto-trigger
7. ✅ Monitor first few builds
8. ✅ Scale to production

---

## Support

For issues or questions:
1. Check **Console Output** for error messages
2. Review test results in Jenkins
3. Check Docker logs: `docker logs <container-id>`
4. Verify all prerequisites are installed
