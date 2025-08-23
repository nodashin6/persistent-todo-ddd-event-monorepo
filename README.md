# TODO Application

## Overview

This is a TODO application that uses a message queue for all server-side processing. The application features a persistent data structure for the `todos` data, allowing for a complete history of all changes.

## Tech Stack

- **Backend**: Python 3.12 with FastAPI
- **Frontend**: Next.js with React and Tailwind CSS v4
- **Database**: Supabase (self-hosted PostgreSQL)
- **Message Queue**: pgmq (a Supabase extension for message queues)
- **Containerization**: Docker and Docker Compose

## Architecture

The application is composed of three main components: a frontend, a backend, and a database with a message queue.

### Frontend

The frontend is a Next.js application that provides the user interface for managing todos. It communicates with the backend via a REST API.

### Backend

The backend is a FastAPI application that exposes a REST API for the frontend. All write operations (create, update, delete) are handled by publishing messages to a `pgmq` message queue. The backend does not directly write to the database tables.

#### Backend Architecture Details

The backend is structured following the principles of **Clean Architecture** and **Domain-Driven Design (DDD)**. The code is organized into four distinct layers:

-   **`domain`**: Contains the core business logic, including domain models (Aggregates, Entities), events, and repository interfaces. This layer has no dependencies on other layers.
-   **`application`**: Contains application-specific logic. It uses domain models and repositories to perform tasks. This layer defines the `AbstractUnitOfWork` and includes application services that orchestrate the business logic.
-   **`infrastructure`**: Contains the implementation details for external concerns like databases, message queues, etc. It provides concrete implementations of the repository interfaces defined in the domain layer and the Unit of Work from the application layer.
-   **`presentation`**: The outermost layer, responsible for presenting data to the user and handling user input. In this case, it's the FastAPI application, defining API endpoints and handling HTTP requests and responses.

This separation of concerns makes the application more modular, testable, and maintainable.

#### Unit of Work (UoW)

The application uses the **Unit of Work pattern** to manage transactions. The `AbstractUnitOfWork` provides an interface for committing or rolling back a set of operations as a single atomic unit. This ensures data consistency across different repositories and services. Both a `SQLAlchemyUnitOfWork` (for production) and an `InMemoryUnitOfWork` (for testing) are implemented.

#### Asynchronous Operations

As described, write operations like creating a `Todo` are handled asynchronously via a message queue (`pgmq`). A dedicated worker process listens to the queue and processes messages, decoupling the API from the database writes and improving responsiveness.

### Database

The database is a self-hosted Supabase instance (PostgreSQL). It contains the tables for the application and the `pgmq` extension for the message queue.

### Message Queue

All server-side processing is done via a message queue using `pgmq`. When a user action requires a change to the database, the backend publishes a message to a queue. A separate worker process (or a database trigger) consumes messages from the queue and performs the necessary database operations.

## Implemented Features (Backend)

The backend currently supports the following features:

-   **User Authentication**:
    -   User registration (`POST /users/`).
    -   Login to get a JWT access token (`POST /token`).
-   **Todos**:
    -   Create, read, update, delete Todos.
    -   All Todo endpoints are protected and user-specific.
-   **Subtasks**:
    -   Create, update, delete Subtasks for a given Todo.
    -   Endpoints are nested under `/todos/{todo_id}/subtasks/`.

## Testing

The backend includes a comprehensive test suite using `pytest`.

### Testing Strategy

To ensure tests are fast, reliable, and independent of external services, the test suite runs against an **in-memory backend**.

-   **In-Memory Repositories**: Concrete repository implementations that store data in Python dictionaries instead of a database.
-   **In-Memory Unit of Work**: A test-specific `InMemoryUnitOfWork` that uses the in-memory repositories and a mock message queue.
-   **Dependency Injection Overrides**: FastAPI's dependency override mechanism is used to swap the real `SQLAlchemyUnitOfWork` with the `InMemoryUnitOfWork` during testing. This allows the same application code to be tested against a fake backend.

### Running Tests

To run the tests, navigate to the `backend/monorepo/todo_app` directory and run:

```bash
pytest
```

## Data Model

The application uses two tables to store the `todos` data:

### `todos` table (standard table)

This table stores the current state of each todo item.

- `id`: a unique identifier for the todo item
- `task`: the description of the todo item
- `is_completed`: a boolean indicating whether the todo is completed
- `created_at`: the timestamp when the todo was created
- `updated_at`: the timestamp of the last update (epoch seconds)

### `p_todos` table (persistent table)

This table stores the history of all changes to the todo items, implementing a persistent data structure.

- `id`: a unique identifier for the record (not the todo item)
- `todo_id`: a foreign key to the `todos` table
- `task`: the description of the todo item
- `is_completed`: a boolean indicating whether the todo is completed
- `created_at`: the timestamp when the todo was created
- `updated_at`: the timestamp of the last update
- `validate_from`: the timestamp from which this version of the record is valid (epoch seconds)
- `validate_to`: the timestamp until which this version of the record is valid (epoch seconds)

## Workflow

The workflow for creating or updating a todo item is as follows:

1.  The user performs an action in the frontend (e.g., creates a new todo).
2.  The frontend sends a request to the backend API.
3.  The backend publishes a message to the `pgmq` message queue. The message contains the details of the action to be performed.
4.  A consumer process (which can be a database trigger or a separate worker) reads the message from the queue.
5.  The consumer updates the `todos` table with the new data.
6.  Upon successful update of the `todos` table, the consumer updates the `p_todos` table to reflect the change, maintaining the history.
    - The `validate_to` of the previous record for the same `todo_id` is set to the `updated_at` value of the new record in the `todos` table.
    - A new record is inserted into `p_todos` with the new data, and its `validate_from` is set to the `updated_at` value.

This workflow ensures that all changes are processed asynchronously and that the history of all changes is preserved.