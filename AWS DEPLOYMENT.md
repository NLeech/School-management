# Deploying to AWS

See https://docs.docker.com/cloud/ecs-integration/  for deploying Docker containers on ECS

Login to docker hub:

```
docker login
```

Build images:

```
docker compose build
```

Pull images to the docker hub:

```
docker push leechlab/school-management:latest
docker push leechlab/sm_postgres_db:latest
```

Create AWS context:

```
docker context create ecs school-management
docker context use  school-management
```

Optionally, you can fill the database with random data for the first container run. 
For this run your container with the command:
```
docker compose --profile fill up
```

Run application:

```
docker compose up
```

If you want to have static IP, please read the following instruction: https://aws.amazon.com/ru/premiumsupport/knowledge-center/alb-static-ip/ and create a Target Group with, an Elastic IP address and a Network Load Balancer. 

Rolling update:

To update your application without interrupting production flow you can simply use
```
docker compose up
```
on the updated Compose project. Your ECS services are created with rolling update configuration. As you run docker compose up with a modified Compose file, the stack will be updated to reflect changes, and if required, some services will be replaced. This replacement process will follow the rolling-update configuration set by your services deploy.update_config configuration.
AWS ECS uses a percent-based model to define the number of containers to be run or shut down during a rolling update. The Docker Compose CLI computes rolling update configuration according to the parallelism and replicas fields. However, you might prefer to directly configure a rolling update using the extension fields x-aws-min_percent and x-aws-max_percent. The former sets the minimum percent of containers to run for service, and the latter sets the maximum percent of additional containers to start before previous versions are removed.
By default, the ECS rolling update is set to run twice the number of containers for a service (200%), and has the ability to shut down 100% containers during the update.

View application logs:

The Docker Compose CLI configures AWS CloudWatch Logs service for your containers. By default you can see logs of your compose application the same way you check logs of local deployments:
```
 docker compose logs
```

Stop application:

```
docker compose down
```
Before stopping your application, remember to deregister your Application Load Balancer from the manually created Target Group if you created it previously.