1.  Create EC2 instance:

  Pick an instance, say t2.medium, 20 GB EBS)
  Make sure Public-IP is Enabled
  Make sure to pick or setup proper SG and PEM

2. Install Docker

  Login to EC2 as ec2-user
  sudo amazon-linux-extras install docker
  sudo service docker start
  sudo chkconfig docker on
  sudo usermod -a -G docker ec2-user
Logout and log back to EC2 (so usermod settings take effect)

  As an alternative, you could install Docker using:
  #sudo yum update -y
  #sudo yum install -y docker
  #sudo systemctl start docker
  #sudo systemctl enable docker
  #sudo systemctl status docker
  #sudo usermod -a -G docker ec2-user

3. Install Minikube

  curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube
  sudo cp minikube /usr/local/bin && rm minikube

4. Install Kubectl etc.

  Create Repo for Kubectl. 
  sudo vi /etc/yum.repos.d/kubernetes.repo
  Update this file with the following content:
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg

  sudo yum install -y kubeadm kubelet kubectl --disableexcludes=kubernetes

5. minikube start --vm-driver=none 
