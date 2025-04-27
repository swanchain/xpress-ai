# Xpress AI

A comprehensive platform integrating AI capabilities with blockchain technology.

## Project Overview

Xpress AI is a modern application that combines AI-powered features with blockchain integration. The project follows a modular architecture with three main components:

- **Frontend**: React-based web application with Next.js
- **Backend**: FastAPI-powered Python backend service
- **Smart Contracts**: Hardhat-based Ethereum smart contracts

## Architecture

### Frontend (Next.js)
The frontend is built using Next.js and provides a responsive user interface for interacting with the platform.

- `/src/components`: Reusable UI components
- `/src/app`: Page components and layouts
- `/src/context`: React context providers
- `/src/hooks`: Custom React hooks
- `/src/services`: API services and utilities
- `/src/abi`: Blockchain ABI definitions
- `/src/config`: Configuration files

### Backend (FastAPI)
The backend provides RESTful API services and handles business logic, data storage, and AI processing.

- `/app/api`: API endpoints
- `/app/auth`: Authentication and authorization
- `/app/database`: Database connection and utilities
- `/app/models`: Database models
- `/app/schemas`: Pydantic schemas for request/response validation
- `/app/services`: Business logic services
- `/app/worker`: Background task processing

Database migrations are managed with Alembic.

### Blockchain (Hardhat)
Smart contracts are developed and tested using the Hardhat framework.

- `/contracts`: Smart contract source code
- `/ignition/modules`: Deployment modules
- `/test`: Smart contract tests

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.9+)
- PostgreSQL
- Ethereum wallet (MetaMask recommended)

### Installation

1. Clone the repository
   ```
   git clone https://github.com/your-username/xpress-ai.git
   cd xpress-ai
   ```

2. Install and run the backend
   ```
   cd backend
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. Install and run the frontend
   ```
   cd frontend
   npm install
   npm run dev
   ```

4. Setup and deploy smart contracts (optional)
   ```
   cd hardhat
   npm install
   npx hardhat compile
   ```

## Features

- AI-powered data analysis and insights
- Secure blockchain integration
- User authentication and authorization
- Real-time updates and notifications

## License

[License information]

## Contact

[Contact information] 