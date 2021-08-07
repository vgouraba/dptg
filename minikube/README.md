1.  Create EC2 instance:

  Pick an instance, say t2.medium, 20 GB EBS)<br /> 
  Make sure Public-IP is Enabled<br /> 
  Make sure to pick or setup proper SG and PEM<br /> 

2. Install Docker

  Login to EC2 as ec2-user<br /> 
  sudo amazon-linux-extras install docker<br /> 
  sudo service docker start<br /> 
  sudo chkconfig docker on<br /> 
  sudo usermod -a -G docker ec2-user<br /><br /> 
Logout and log back to EC2 (so usermod settings take effect)<br /> 

  As an alternative, you could install Docker using:<br /> 
  #sudo yum update -y <br /> 
  #sudo yum install -y docker <br /> 
  #sudo systemctl start docker <br /> 
  #sudo systemctl enable docker <br /> 
  #sudo systemctl status docker <br /> 
  #sudo usermod -a -G docker ec2-user <br /> 

3. Install Minikube

  curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube <br /> 
  sudo cp minikube /usr/local/bin && rm minikube <br /> 

4. Install Kubectl etc.

  Create Repo for Kubectl. <br />
  sudo vi /etc/yum.repos.d/kubernetes.repo <br /> <br /> 
  Update this file with the following content: <br /> 
    [kubernetes]<br /> 
    name=Kubernetes<br /> 
    baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64<br /> 
    enabled=1<br /> 
    gpgcheck=1<br /> 
    repo_gpgcheck=1<br /> 
    gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg<br />

  sudo yum install -y kubeadm kubelet kubectl --disableexcludes=kubernetes<br /> 

5. minikube start --vm-driver=none 
