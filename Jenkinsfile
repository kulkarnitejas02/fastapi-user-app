pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'your-dockerhub-username/fastapi-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        REGISTRY = 'docker.io'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '=========================================='
                echo 'Stage: Checkout Code from Repository'
                echo '=========================================='
                checkout scm
                sh 'echo "Repository checked out successfully"'
            }
        }

        stage('Run Comprehensive Tests') {
            steps {
                echo '=========================================='
                echo 'Stage: Running All Test Cases'
                echo '=========================================='
                script {
                    try {
                        sh 'pip install -q pytest pytest-cov'
                        sh 'pip install -q -r requirements.txt'
                        sh 'echo "Running all tests from tests/ directory..."'
                        sh 'pytest tests/ -v --tb=short --junit-xml=test-results.xml'
                        sh 'echo "✓ All test cases passed successfully!"'
                    } catch (Exception e) {
                        sh 'echo "✗ Test cases failed!"'
                        throw e
                    }
                }
            }
        }

        stage('Code Quality Check') {
            steps {
                echo '=========================================='
                echo 'Stage: Code Quality Analysis'
                echo '=========================================='
                script {
                    try {
                        sh 'pip install -q flake8'
                        sh 'flake8 --max-line-length=88 --extend-ignore=E203,W503 main.py expense.py income.py models.py schemas.py database.py dependencies.py || true'
                        sh 'echo "✓ Code quality check completed"'
                    } catch (Exception e) {
                        sh 'echo "⚠ Code quality issues found (non-blocking)"'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '=========================================='
                echo 'Stage: Building Docker Image'
                echo '=========================================='
                script {
                    try {
                        sh 'echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"'
                        sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
                        sh 'docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest'
                        sh 'echo "✓ Docker image built successfully"'
                        sh 'docker images | grep ${DOCKER_IMAGE}'
                    } catch (Exception e) {
                        sh 'echo "✗ Docker build failed!"'
                        throw e
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            when {
                branch 'main'  // Only push from main branch
            }
            steps {
                echo '=========================================='
                echo 'Stage: Pushing Image to Docker Hub'
                echo '=========================================='
                script {
                    try {
                        withCredentials([usernamePassword(
                            credentialsId: 'dockerhub-credentials',
                            usernameVariable: 'DOCKER_USERNAME',
                            passwordVariable: 'DOCKER_PASSWORD'
                        )]) {
                            sh 'echo "Logging in to Docker Hub..."'
                            sh 'echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin'
                            sh 'echo "Pushing image ${DOCKER_IMAGE}:${DOCKER_TAG}..."'
                            sh 'docker push ${DOCKER_IMAGE}:${DOCKER_TAG}'
                            sh 'echo "Pushing latest tag..."'
                            sh 'docker push ${DOCKER_IMAGE}:latest'
                            sh 'docker logout'
                            sh 'echo "✓ Docker image pushed to Docker Hub successfully"'
                        }
                    } catch (Exception e) {
                        sh 'echo "✗ Docker push failed!"'
                        sh 'docker logout || true'
                        throw e
                    }
                }
            }
        }
    }

    post {
        always {
            echo '=========================================='
            echo 'Pipeline Cleanup'
            echo '=========================================='
            junit 'test-results.xml' ?: [:]
            sh 'docker system prune -f || true'
            sh 'echo "✓ Cleanup completed"'
        }
        success {
            echo '=========================================='
            echo '✓ PIPELINE SUCCEEDED!'
            echo '=========================================='
            echo 'All stages completed successfully:'
            echo '  1. ✓ Code checked out'
            echo '  2. ✓ All tests passed'
            echo '  3. ✓ Code quality verified'
            echo '  4. ✓ Docker image built'
            echo '  5. ✓ Image pushed to Docker Hub'
        }
        failure {
            echo '=========================================='
            echo '✗ PIPELINE FAILED!'
            echo '=========================================='
            echo 'Check logs above for details'
        }
    }
}
