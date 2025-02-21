# Step-by-Step Guide: FastAPI Cocktail API with Docker
<small>based on [Link](https://bakshiharsh55.medium.com/deploy-python-fastapi-using-azure-container-registry-71c332f88ffb)</small>

## 1. Project Setup
bash
mkdir fastapi-cocktails
Create the basic project structure:
```bash
mkdir fastapi-cocktails
cd fastapi-cocktails
```

### Project structure:

```
/
├── README.md
├── Dockerfile
├── main.py
├── requirements.txt
├── .env
├── .dockerignore
├── models/
│   └── (model files)
├── services/
│   └── (service files)
└── data/
    └── (JSON files)
```

## 2. Create Dockerfile
```dockerfile
FROM python:3.11

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code and data
COPY main.py .
COPY models/ ./models/
COPY services/ ./services/
COPY data/ ./data/

# Make sure the directories are accessible
RUN chmod -R 755 ./data ./models ./services

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

```

## 3. Create .dockerignore

```txt
.env
__pycache__
*.pyc
.git

```
## 4. Build Docker Image
```bash
docker build -t cocktail-api .
```
## 5. Run the Container
With environment variables from .env file:
```bash
docker run -p 8000:80 --env-file ./.env cocktail-api
```
Or with specific environment variables:
```bash
docker run -p 8000:80 -e AUTH_TOKEN=your_token cocktail-api
```
## 6. Access the API locally 

The API will be available at:

- http://localhost:8000 / 127.0.0.1:8000

- http://localhost:8000/docs (Swagger UI)

<details> <summary> Useful Docker Commands</summary>
Check running containers:
```bash
docker ps
```
Stop a container:
```bash
docker stop <container-id>
```
Check container logs:
```bash
docker logs <container-id>
```
Access container shell:
```bash
docker exec -it <container-id> /bin/bash
```

</details>
<details> <summary>Troubleshooting</summary>
If Docker isn't running:

1. Start Docker Desktop

2. Wait for it to fully initialize

3. Try building/running again

If port 80 is in use:

- Use a different port mapping (e.g., -p 8000:80)

If environment variables aren't working:

1. Verify .env file exists

2. Check variable names match

3. Use docker exec to verify variables inside container
</details>

## 7 Azure Deployment Steps:

### Step 1: Set up Azure Container Registry (ACR)

1) Log into Azure Portal  
2) Create a new Container Registry  
3) Enable Admin user in the registry settings  

### Step 2: Push your image to ACR

Login to Azure Container Registry:
```bash  
az acr login --name <your-registry-name>  
```
Tag your image:  
```bash
docker tag cocktail-api <your-registry-name>.azurecr.io/cocktail-api:latest  
```
Push to ACR:  
```bash
docker push <your-registry-name>.azurecr.io/cocktail-api:latest  
```
### Step 3: Create an App Service

1) Search for "App Service" in Azure Portal  
2) Click "Create"  
3) Select your subscription and resource group  
4) Configure:  
   - Name: Choose a unique name  
   - Publish: Docker Container  
   - Operating System: Linux  
   - Region: Choose nearest to you  
   - Plan: Select appropriate plan  

### Step 4: Configure Docker

1) In the Docker tab, choose "Single Container"  
2) Image Source: Azure Container Registry  
3) Select your registry, image, and tag  
4) Click "Review + Create"  
5) Click "Create"  

### Step 5: Configure Environment Variables

1) Once deployed, go to your App Service  
2) Navigate to "Configuration"  
3) Add your environment variables (API_KEY, etc.)  
4) Save the changes  

### Step 6: Access Your API

1) Your API will be available at https://<your-app-name>.azurewebsites.net  
2) Test the endpoints to ensure everything works  

### Additional Tips:

- Enable logging in App Service to monitor your application  
- Set up Azure Application Insights for monitoring  
- Consider using deployment slots for zero-downtime deployments  
- Make sure your environment variables are properly configured  
- Monitor your application's performance and scale as needed


## 9. Best Practices
1. Never commit sensitive data to version control

2. Keep Docker image size small

3. Use proper port mapping

4. Handle environment variables securely

5. Use proper permissions in container

6. Always use .dockerignore

## 10. Notes
- 0.0.0.0 in the container means "listen on all interfaces"

- Access via localhost or 127.0.0.1 on host machine

- Port mapping format: -p host_port:container_port

- Environment variables can be passed at runtime

