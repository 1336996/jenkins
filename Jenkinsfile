pipeline {
    environment {
    imagename = "mithilesh/pythonapp"
    registryCredential = 'docker'
    dockerImage = ''
  }
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                // Get some code from a GitHub repository
                git credentialsId: '18b9b159-5153-41a0-ad4f-65acc7d8c08f', url: 'https://github.com/1336996/jenkins.git'
            }

        }
        stage('Build Image') {
            steps {
                script {
                    dockerImage = docker.build imagename
                }
            }
        }
        stage('Push Image') {
            steps{
                script {
                  docker.withRegistry('', registryCredential) {
                    dockerImage.push("$BUILD_NUMBER")
                    dockerImage.push('latest')
                  }
                }
            }
        }
        stage('Deploy Image') {
            steps {
                script {
                    sshagent(credentials : ['ec2']) {
                        docker.withRegistry('', registryCredential) {
                            sh 'ssh -tt ec2-user@3.16.129.77 sudo docker run -d --expose=5000 -p=5000:5000 "${imagename}:latest"'

                            
                        }
                   // sh 'docker run -d --expose=5000 -p=5000:5000 "${imagename}:latest"'
                  }
                }
            }
        }
        stage('Remove Unused docker image') {
        steps{
         sh "docker rmi $imagename:$BUILD_NUMBER"
         sh "docker rmi $imagename:latest"

        }
        }
      
    }
}
