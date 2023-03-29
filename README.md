# Google Kubernetes Engine (GKE), Airflow and Terraform template
# *Project:* airflow-gke-project
 
## Prerequisites
- [Configured GCP account](https://cloud.google.com/)
- [Homebrew](https://brew.sh/) (if you're using MacOS)
- [Kubectl cli](https://kubernetes.io/docs/tasks/tools/) (choose the OS you're working with)
- [gCloud SDK](https://cloud.google.com/sdk/docs/quickstart)
- [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli) >= 0.13
    https://developer.hashicorp.com/terraform/downloads
- [Helm 3](https://helm.sh/docs/intro/install/)

### ***IMPORTANT***: to mention that "LINUX" was used to execute these commands.

## Step by step guide
1. Clone this repository.

2. Create a [virtual environment for your local project](https://medium.com/@dakota.lillie/an-introduction-to-virtual-environments-in-python-ce16cda92853)
and activate it:
    ```bash
    $ python3 -m venv .venv # create virtual environment
    source .venv/bin/activate # activate virtual environment
    deactivate # DO NOT RUN YET: deactivates virtual environment
    ```

3. Initialize gcloud SDK and authorize it to access GCP using your user account credentials:
    ```bash
    $ gcloud init
       
    # The next portion represents the cli settings setup
    >> [1] Re-initialize this configuration [default] with new settings # config to use
    >> [1] user@sample.com # account to perform operations for config
    >> [6] project-id # cloud project to use
     
    >> [8] us-central1-a # region to connect to. set a default computing zone and region based on your location
   
    $ gcloud auth application-default login # authorize access
    ```
   **DISCLAIMER:** This part will ask you to choose the Google account and the GCP project you will work with. It
will also ask you to choose a region to connect to. The information shown above in is an example of what you *can*
choose, but keep in mind that this was used for credentials that were already entered once before. 

3. For GCP to access you user account credentials for the first time, it will ask you to give it explicit permission like so:

![Choose account for Google Cloud SDK](imgs\Screenshot_6.png "Choose account")

![Grant access for Google Cloud SDK](imgs\Screenshot_7.png "Grant access")

4. After choosing the Google account to work with and successfully granting permissions, you should be redirected to this message:

![Successful authentication message](imgs\Screenshot_8.png "Successful authentication")

We copy the code and paste it in the terminal where it is requested

![Authorization code for authentication](imgs\Screenshot_9.png "Authorization code for authentication")





6. In the GCP Console, enable:
   - Compute Engine API
   - Kubernetes Engine API

7. In your cloned local project, copy the [terraform.tfvars.example](./terraform.tfvars.example) and paste it in the
root of the project named as *terraform.tfvars*, changing the property *project_id* to your corresponding project ID.

8. Initialize the Terraform workspace and create the resources:
    ```bash
    $ terraform init # initialize
    $ terraform init --upgrade # if you initialized once before and need to update terraform config
    
    $ terraform apply --var-file=terraform.tfvars
    >> yes # lets terraform perform actions described
    ```
    ***IMPORTANT***: This process might take around 10-15 minutes, **be patient please**.

9. Information about the Kubernetes cluster name and the region where it is located is combined to authenticate and configure the local environment to work with the Kubernetes cluster on GCP:
    ```bash
    $ gcloud container clusters get-credentials $(terraform output -raw kubernetes_cluster_name) --region $(terraform output -raw location)
    ```

10. To work with Airflow, create a NFS (Network File System) server:
     ```bash
     $ kubectl create namespace nfs # creates namespace
     $ kubectl -n nfs apply -f nfs/nfs-server.yaml # creates server
     $ export NFS_SERVER=$(kubectl -n nfs get service/nfs-server -o jsonpath="{.spec.clusterIP}")
     #https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
     ```
    
11. Create a namespace for storage deployment:
     ```bash
     $ kubectl create namespace storage
     ```  
12. Add the chart for the nfs-provisioner:
     ```bash
     $ helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
     #https://helm.sh/docs/intro/install/
     ```

13. Install nfs-external-provisioner:
     ```bash
     $ helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
     --namespace storage \
     --set nfs.server=$NFS_SERVER \
     --set nfs.path=/
     ```
14. Create a namespace for Airflow:
    ```bash
    $ kubectl create namespace airflow
    ```
15. Add the chart repository:
    ```bash
    $ helm repo add apache-airflow https://airflow.apache.org
    ```
16. Install the Airflow chart from the repository:
    ```bash
    $ helm upgrade --install airflow -f airflow-values.yaml apache-airflow/airflow --namespace airflow
    ```

When cloning the file  "airflow-values.yaml" it is important that when you change the URL you want to link to, it must be copied from the URL where your repository is, in this example we have a folder called "dags" and also we add the child path to the .yaml file

![Yaml file modification](imgs\Screenshot_10.png "Yaml file modification")

![Address for modifying yaml file](imgs\Screenshot_12.png "Address for modifying yaml file")

***IMPORTANT***: This process might take around 5 minutes to execute, **be patient please**.



17. Access the Airflow dashboard with what the Helm chart provided:
    ```bash
    Your release is named airflow.
    You can now access your dashboard(s) by executing the following command(s) and visiting the corresponding port at localhost in your browser:
    
    Airflow Webserver:     kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
    Default Webserver (Airflow UI) Login credentials:
        username: admin
        password: admin
    Default Postgres connection credentials:
        username: postgres
        password: postgres
        port: 5432
    ```
    **Note:** Sometimes there's an error when doing the kubectl portforward. If all of the pods are running, we might
    just need to keep trying.
18. Execute the Airflow Webserver commit:
```bash
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
```
Once in `localhost:8080`, you should see the Airflow login.

![Airflow Login](imgs\Screenshot_13.png "Airflow Login")

19. After logging in with your credentials (username and password from webserver in step 18), you should see the Airflow
dashboard.

![Airflow Dashboard](imgs\Screenshot_14.png "Airflow Dashboard")

20. To verify that the PODS are working correctly, open another terminal and execute the following command::
    ```bash
    $ kubectl get pods -n airflow
    ```
![Airflow Pods](imgs\Screenshot_15.png "Airflow Pods")

If one of the PODS does not work correctly, it must be deleted so that it is automatically regenerated, for this we use the following command:

```bash
    $ kubectl delete pod <name pod> --force --grace-period=0 --namespace airflow
```
**Note:** we replace `<name pod>` with the name of the pod we want to replace.

21. It is important to stop and ***destroy the platform*** that has been created when you are no longer using it to avoid additional costs!
- We stop with the commands `ctrl + c`
- To destroy the cluster:
    ```bash
    $ terraform destroy --var-file=terraform.tfvars
    ```
- Double-check your GCP console to make sure everything was correctly destroyed.

    
