# TODO Application

## Overview

This is a TODO application that uses a message queue for all server-side processing. The application features a persistent data structure for the `todos` data, allowing for a complete history of all changes.

## Tech Stack

- **Backend**: Python 3.12 with FastAPI and uv
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

### Database

The database is a self-hosted Supabase instance (PostgreSQL). It contains the tables for the application and the `pgmq` extension for the message queue.

### Message Queue

All server-side processing is done via a message queue using `pgmq`. When a user action requires a change to the database, the backend publishes a message to a queue. A separate worker process (or a database trigger) consumes messages from the queue and performs the necessary database operations.

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