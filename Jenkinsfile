pipeline {
    agent any
environment {
// Environment and namespace to deploy
        NAMESPACE = "core"
        SLACK_CHANNEL = "highlanders-alerts"
        DOCKERHUB_USERNAME = credentials("dockerhub-username")
        DOCKERHUB_PASSWORD = credentials("dockerhub-password")

}

parameters {
        choice(name: 'MYSERVICE', choices: ['ms1', 'ms2','ms4','ms5'], description: 'ms to hit')
        string(name: 'MYSCHEDULESCALEUP', defaultValue: '0 23 13 * * *', description: 'Scaleup cron schedule')
        string(name: 'SCALE_UP_MIN_REPLICA', defaultValue: '20', description: 'raise minreplica to')
        string(name: 'SCALE_DOWN_AFTER_HOURS', defaultValue: '', description: 'return back to normal after hours')
    }
    stages {
        stage('Checkout proj') {
        steps {
            git branch: 'master',
                url: 'https://github.com/uday-kakkar/scheduled-scaling.git/'
            }
        }
        stage('Hello') {
            steps {
                sh "python generate-kube-spec.py -s ${MYSERVICE} -u \"${MYSCHEDULESCALEUP}\" -k \"${SCALE_DOWN_AFTER_HOURS}\" -m ${SCALE_UP_MIN_REPLICA} -t template-scaleup-down-replicas.yml"
            }
        }
        stage('Apply Kube') {
            steps {
                sh "kubectl --context=\"qa.k8s.ssense.com\" apply -f to_apply"
            }
    }    }
}
