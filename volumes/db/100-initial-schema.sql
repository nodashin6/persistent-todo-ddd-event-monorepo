-- Enable pgmq extension
create extension if not exists pgmq with schema extensions;

-- Create the todos table
create table todos (
  id bigserial primary key,
  task text not null,
  is_completed boolean default false,
  created_at timestamptz default now() not null,
  updated_at bigint not null
);

-- Create the p_todos table for persistent data
create table p_todos (
  id bigserial primary key,
  todo_id bigint not null,
  task text not null,
  is_completed boolean not null,
  created_at timestamptz not null,
  updated_at bigint not null,
  validate_from bigint not null,
  validate_to bigint
);

-- Create an index on todo_id for faster lookups
create index on p_todos (todo_id);

-- Create the message queue for todos
select pgmq.create('todo_queue');
