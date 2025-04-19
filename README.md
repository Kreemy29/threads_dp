# Caption Generator API

> **IMPORTANT**: This application requires valid API keys for DeepSeek, Weather API, and Ticketmaster. Make sure to set these in your `.env` file before running the application.

This API generates engaging social media captions based on location, incorporating real-time data from weather, news, and events APIs.

## Features

- Three types of captions:
  - **Baity**: Attention-grabbing captions incorporating weather or news data
  - **Opinion**: Thoughtful captions that reference local news headlines
  - **Event**: Captions focused on local events and concerts

- Each caption is unique and relates to the provided location
- Captions are enhanced with AI through the DeepSeek API

## Installation

### Standard Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   cp .env.example .env
   # Edit .env with your API keys
   ```
4. Make sure all required API keys are set in the `.env` file:
   - `DEEPSEEK_API_KEY` for the DeepSeek AI API
   - `WEATHER_API_KEY` for weather data
   - `TICKETMASTER_API_KEY` for event data

### Docker Installation

1. Clone this repository
2. Copy the environment file and fill in your API keys:
   ```
   cp .env.example .env
   # Edit .env with your API keys
   ```
3. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

## Usage

### Starting the API Server

#### Standard Method
Run the following command:

```
python api.py
```

#### Using Docker
If you're using Docker, the server starts automatically when you run:
```
docker-compose up -d
```

This will start the FastAPI server on http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

### API Endpoints

#### POST /generate

Generate a new caption based on location and number.

**Request Body:**

```json
{
  "location": "New York",
  "number": 1
}
```

Parameters:
- `location`: Any location name (city, state, country)
  - For baity captions: Used to fetch local weather or news
  - For opinion captions: Used to fetch local news headlines
  - For event captions: Used to search for events at the specified location (falls back to searching major US cities if no events found)
- `number`: A number from 1-10+
  - 1, 4, 7, 10... generate baity captions
  - 2, 5, 8... generate opinion captions
  - 3, 6, 9... generate event captions

**Response:**

```json
{
  "caption": "The generated caption text",
  "caption_type": "baity"
}
```

### Testing the API

You can use the included client example to test the API:

```
python client_example.py "Chicago"
```

This will generate three captions (one of each type) for Chicago.

## Deployment

### Cloud Deployment Options

#### Deploying to Heroku

1. Create a new Heroku app
2. Add the necessary environment variables (API keys) in Heroku settings
3. Deploy using the Heroku CLI or GitHub integration:
   ```
   heroku container:push web -a your-app-name
   heroku container:release web -a your-app-name
   ```

#### Deploying to AWS

1. Push your Docker image to Amazon ECR:
   ```
   aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
   docker tag caption-api:latest aws_account_id.dkr.ecr.region.amazonaws.com/caption-api:latest
   docker push aws_account_id.dkr.ecr.region.amazonaws.com/caption-api:latest
   ```

2. Deploy using ECS or Fargate

#### Deploying to Google Cloud

1. Push your Docker image to Google Container Registry:
   ```
   docker tag caption-api:latest gcr.io/your-project-id/caption-api:latest
   docker push gcr.io/your-project-id/caption-api:latest
   ```

2. Deploy to Google Cloud Run:
   ```
   gcloud run deploy caption-api --image gcr.io/your-project-id/caption-api:latest --platform managed
   ```

## Environment Variables

The following environment variables can be set:

- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `WEATHER_API_KEY`: Your Weather API key
- `TICKETMASTER_API_KEY`: Your Ticketmaster API key
- `DATA_DIR`: Directory for caption data files (default: `./data`)

## Example

Request:
```
POST /generate
{
  "location": "Miami",
  "number": 1
}
```

Response:
```
{
  "caption": "Is it hot and sunny in Miami, or is it just you making it hot? 🔥 Let's turn up the heat!",
  "caption_type": "baity"
}
```

## Configuration

Adjust settings in `config.py`:
- API keys for external services
- File paths for caption templates

## License

This project is licensed under the MIT License.