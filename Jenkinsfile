// Jenkins Pipeline Configuration for Notification E2E Suite
// Supports:
// - Headless browser mode
// - Parallel test execution
// - Test artifact collection
// - Multiple Python versions
// - Exit code handling

pipeline {
    agent any
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
    }
    
    parameters {
        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'webkit', 'all'],
            description: 'Browser engine to use for testing'
        )
        choice(
            name: 'PARALLEL_WORKERS',
            choices: ['1', '2', '4', '8'],
            description: 'Number of parallel workers for test execution'
        )
        booleanParam(
            name: 'SKIP_PROPERTY_TESTS',
            defaultValue: false,
            description: 'Skip property-based tests (for faster builds)'
        )
    }
    
    environment {
        PLAYWRIGHT_HEADLESS = '1'
        CI = 'true'
        PYTHON_VERSION = '3.11'
        REPORTS_DIR = 'tests/reports'
        SCREENSHOTS_DIR = 'tests/reports/screenshots'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    echo "✓ Code checkout complete"
                    echo "  Branch: ${env.GIT_BRANCH}"
                    echo "  Commit: ${env.GIT_COMMIT}"
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo "Setting up test environment..."
                    sh '''
                        python3 --version
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest-xdist
                        echo "✓ Python dependencies installed"
                    '''
                }
            }
        }
        
        stage('Install Playwright') {
            steps {
                script {
                    echo "Installing Playwright browsers in headless mode..."
                    sh '''
                        playwright install --with-deps
                        echo "✓ Playwright browsers installed for headless execution"
                    '''
                }
            }
        }
        
        stage('Run Tests - Chromium') {
            when {
                expression { params.BROWSER == 'chromium' || params.BROWSER == 'all' }
            }
            steps {
                script {
                    echo "Running E2E tests with Chromium (headless mode)..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            pytest \
                                --browser chromium \
                                --html=${REPORTS_DIR}/test_report_chromium.html \
                                --self-contained-html \
                                -n ${PARALLEL_WORKERS} \
                                -v \
                                --tb=short
                            TEST_EXIT=$?
                            echo "Test exit code: $TEST_EXIT"
                            exit $TEST_EXIT
                        '''
                    }
                }
            }
        }
        
        stage('Run Tests - Firefox') {
            when {
                expression { params.BROWSER == 'firefox' || params.BROWSER == 'all' }
            }
            steps {
                script {
                    echo "Running E2E tests with Firefox (headless mode)..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            pytest \
                                --browser firefox \
                                --html=${REPORTS_DIR}/test_report_firefox.html \
                                --self-contained-html \
                                -n ${PARALLEL_WORKERS} \
                                -v \
                                --tb=short
                            TEST_EXIT=$?
                            exit $TEST_EXIT
                        '''
                    }
                }
            }
        }
        
        stage('Run Tests - WebKit') {
            when {
                expression { params.BROWSER == 'webkit' || params.BROWSER == 'all' }
            }
            steps {
                script {
                    echo "Running E2E tests with WebKit (headless mode)..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            pytest \
                                --browser webkit \
                                --html=${REPORTS_DIR}/test_report_webkit.html \
                                --self-contained-html \
                                -n ${PARALLEL_WORKERS} \
                                -v \
                                --tb=short
                            TEST_EXIT=$?
                            exit $TEST_EXIT
                        '''
                    }
                }
            }
        }
        
        stage('Run Property-Based Tests') {
            when {
                expression { !params.SKIP_PROPERTY_TESTS }
            }
            steps {
                script {
                    echo "Running property-based tests with parallel execution..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            pytest tests/property/ \
                                --browser chromium \
                                --html=${REPORTS_DIR}/property_report.html \
                                --self-contained-html \
                                -n ${PARALLEL_WORKERS} \
                                -v \
                                --tb=short
                            TEST_EXIT=$?
                            exit $TEST_EXIT
                        '''
                    }
                }
            }
        }
        
        stage('Run Parallel Tests') {
            steps {
                script {
                    echo "Running tests with ${PARALLEL_WORKERS} parallel workers..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            pytest \
                                -n ${PARALLEL_WORKERS} \
                                --dist loadscope \
                                --html=${REPORTS_DIR}/parallel_report.html \
                                --self-contained-html \
                                -v \
                                --tb=short
                            TEST_EXIT=$?
                            exit $TEST_EXIT
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "Collecting test artifacts and reports..."
                
                // Archive HTML reports
                archiveArtifacts(
                    artifacts: '${REPORTS_DIR}/**/*.html',
                    allowEmptyArchive: true,
                    fingerprint: true
                )
                
                // Archive screenshots
                archiveArtifacts(
                    artifacts: '${SCREENSHOTS_DIR}/**/*.png',
                    allowEmptyArchive: true,
                    fingerprint: false
                )
                
                // Publish HTML reports
                publishHTML([
                    reportDir: '${REPORTS_DIR}',
                    reportFiles: 'test_report_chromium.html,test_report_firefox.html,test_report_webkit.html,property_report.html,parallel_report.html',
                    reportName: 'E2E Test Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true
                ])
            }
            
            // Clean workspace
            cleanWs(deleteDirs: true, patterns: [[pattern: '.pytest_cache', type: 'INCLUDE']])
        }
        
        success {
            script {
                echo "✓ All tests passed successfully"
                // Send success notification
                sh '''
                    echo "✓ Test execution completed successfully"
                    echo "  - Headless browser mode: enabled"
                    echo "  - Exit code: 0 (success)"
                    echo "  - Artifacts: ${REPORTS_DIR}/"
                    echo "  - Screenshots: ${SCREENSHOTS_DIR}/"
                '''
            }
        }
        
        unstable {
            script {
                echo "⚠ Some tests failed or were unstable"
                sh '''
                    echo "⚠ Test execution encountered failures"
                    ls -la ${REPORTS_DIR}/ || echo "Reports directory not found"
                '''
            }
        }
        
        failure {
            script {
                echo "✗ Build failed"
                sh '''
                    echo "✗ Test execution failed"
                    echo "  - Exit code: non-zero (failure)"
                    echo "  - Check reports at ${REPORTS_DIR}/"
                '''
            }
        }
    }
}
