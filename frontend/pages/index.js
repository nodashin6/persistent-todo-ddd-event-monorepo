import Head from 'next/head'
import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Home() {
  const [todos, setTodos] = useState([])
  const [task, setTask] = useState('')

  const fetchTodos = async () => {
    try {
      const res = await axios.get('http://localhost:8001/todos/')
      setTodos(res.data)
    } catch (error) {
      console.error(error)
    }
  }

  useEffect(() => {
    fetchTodos()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('http://localhost:8001/todos/', { task })
      setTask('')
      // After a short delay, fetch the todos again to see the new todo.
      // In a real app, you might use websockets or a more sophisticated state management.
      setTimeout(fetchTodos, 1000)
    } catch (error) {
      console.error(error)
    }
  }

  const handleComplete = async (todoId) => {
    try {
      await axios.post(`http://localhost:8001/todos/${todoId}/complete`)
      setTimeout(fetchTodos, 1000)
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <Head>
        <title>Todo App</title>
        <meta name="description" content="Todo App" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1 className="text-2xl font-bold mb-4">
          Todo App
        </h1>

        <form onSubmit={handleSubmit} className="mb-4">
          <input
            type="text"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="New todo..."
            className="border p-2 mr-2"
          />
          <button type="submit" className="bg-blue-500 text-white p-2">Add Todo</button>
        </form>

        <ul>
          {todos.map((todo) => (
            <li key={todo.id} className={`border-b p-2 flex justify-between items-center ${todo.is_completed ? 'line-through text-gray-500' : ''}`}>
              <span>{todo.task}</span>
              {!todo.is_completed && (
                <button onClick={() => handleComplete(todo.id)} className="bg-green-500 text-white p-1 text-xs">
                  Complete
                </button>
              )}
            </li>
          ))}
        </ul>
      </main>
    </div>
  )
}
