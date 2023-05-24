## Running the application locally

### Prerequisites

- Python 3.11
- Pipenv
- Google Cloud credentials JSON file

### Installing dependencies

1. Install Pipenv by running the following command:

```
pip install pipenv
```

2. Install the dependencies by running the following command:

```
pipenv install
```

3. Activate the virtual environment by running the following command:

```
pipenv shell
```

### Running the application using a user account

1. Log in to your Google account by running the following command:

```
gcloud auth login
```

2. Run the application by running the following command:

```
python src/fetch_data.py
```

### Running the application using a Service Account

1. Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of your Google Cloud credentials JSON file:

```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

Replace `/path/to/credentials.json` with the path to your Google Cloud credentials JSON file on your local machine.

2. Run the application by running the following command:

```
python src/fetch_data.py
```

## Running the application in a Docker container

### Prerequisites

- Docker
- Google Cloud credentials JSON file

### Building and running the Docker image

To run the Dockerfile and pass an environment variable, you need to build the Docker image, create a container, and then run the container with the environment variable.

1. Build the Docker image by running the following command:

```
docker build -t game_prediction .
```

Replace `game_prediction` with the desired name for your Docker image.

2. Run a container from the built image and pass the environment variable `GOOGLE_APPLICATION_CREDENTIALS`:

```
docker run -e GOOGLE_APPLICATION_CREDENTIALS=/app/app_key.json -v /path/to/credentials.json:/app/app_key.json game_prediction
```

Replace `/path/to/credentials.json` with the path to your Google Cloud credentials JSON file on your local machine. The `-v` flag is used to mount the credentials file inside the container.

This command will create and run a container with the environment variable `GOOGLE_APPLICATION_CREDENTIALS` set to the specified path.
