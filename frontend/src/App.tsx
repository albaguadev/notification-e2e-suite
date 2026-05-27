import './App.css'
import NotificationForm from './components/NotificationForm'
import NotificationQuery from './components/NotificationQuery'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Notification E2E Suite</h1>
      </header>
      <main className="app-main">
        <NotificationForm />
        <NotificationQuery />
      </main>
    </div>
  )
}

export default App
