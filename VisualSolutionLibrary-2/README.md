# Visual Solution Library

A Streamlit-based application for students to share, explore, and comment on assignment solutions with step-by-step playback functionality.

## Features

- Upload and store solution files
- Visually display solutions with detailed descriptions
- Browse and explore the solution library
- Step-by-step solution playback visualization
- Rate solutions (1-5 stars)
- Comment on solutions
- Search and filter solutions by category/tag
- Simple user management

## Setup and Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

3. Access the application at `http://localhost:5000`

## Project Structure

- `app.py`: Main application entry point
- `utils.py`: Utility functions
- `components.py`: UI components and widgets
- `authentication.py`: User authentication functionality
- `data_manager.py`: Data management and storage
- `data/`: Directory for storing solution files and metadata
