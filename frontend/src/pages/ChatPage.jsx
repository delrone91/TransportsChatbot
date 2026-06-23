import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import MessageInput from '../components/MessageInput'
import './ChatPage.css'

export default function ChatPage() {
  const { user, logout } = useAuth()
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [sending, setSending] = useState(false)

  async function fetchSessions() {
    try {
      const r = await client.get('/chat/sessions')
      setSessions(r.data)
    } catch {
      setSessions([])
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchSessions()
  }, [])

  const createSession = async () => {
    const r = await client.post('/chat/sessions', {})
    setSessions(prev => [r.data, ...prev])
    setActiveSession(r.data)
    setMessages([])
  }

  const selectSession = async (session) => {
    if (activeSession?.id === session.id) return
    setActiveSession(session)
    setMessages([])
    const r = await client.get(`/chat/sessions/${session.id}`)
    setMessages(r.data.messages)
  }

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation()
    await client.delete(`/chat/sessions/${sessionId}`)
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (activeSession?.id === sessionId) {
      setActiveSession(null)
      setMessages([])
    }
  }

  const sendMessageToSession = async (session, content, useWeb = false) => {
    const tempId = Date.now()
    setMessages(prev => [...prev, { id: tempId, role: 'user', content }])
    setSending(true)
    try {
      const r = await client.post(`/chat/sessions/${session.id}/messages`, { content, use_web: useWeb })
      setMessages(prev => [
        ...prev.filter(m => m.id !== tempId),
        r.data.user_message,
        r.data.assistant_message,
      ])
      const newTitle = r.data.session_title
      setSessions(prev => prev.map(s => s.id === session.id ? { ...s, title: newTitle } : s))
      setActiveSession(prev => ({ ...prev, title: newTitle }))
    } catch {
      setMessages(prev => prev.filter(m => m.id !== tempId))
    } finally {
      setSending(false)
    }
  }

  const sendMessage = async (content, useWeb = false) => {
    if (!activeSession || sending) return
    await sendMessageToSession(activeSession, content, useWeb)
  }

  const createSessionAndSend = async (content) => {
    if (sending) return
    const r = await client.post('/chat/sessions', {})
    const newSession = r.data
    setSessions(prev => [newSession, ...prev])
    setActiveSession(newSession)
    setMessages([])
    await sendMessageToSession(newSession, content)
  }

  return (
    <div className="chat-layout">
      <Sidebar
        sessions={sessions}
        activeSession={activeSession}
        user={user}
        onSelect={selectSession}
        onCreate={createSession}
        onDelete={deleteSession}
        onLogout={logout}
      />
      <main className="chat-main">
        {activeSession ? (
          <>
            <header className="chat-header">
              <h2>{activeSession.title}</h2>
            </header>
            <ChatWindow messages={messages} sending={sending} />
            <MessageInput onSend={sendMessage} disabled={sending} />
          </>
        ) : (
          <div className="chat-empty">
            <div className="empty-kicker">
              <img src="/logo.png" alt="NavigIA" />
              <span>NavigIA</span>
            </div>
            <h2 className="empty-title">Infos transports, sans tourner en rond.</h2>
            <p className="empty-subtitle">
              Tarifs, gares, accessibilite et donnees SNCF/IDFM dans une interface simple a consulter.
            </p>
            <p className="suggestions-label">Questions utiles</p>
            <div className="empty-suggestions">
              <button className="suggestion" onClick={() => createSessionAndSend('Quel est le prix du forfait Navigo mensuel ?')}>
                Quel est le prix du forfait Navigo mensuel ?
              </button>
              <button className="suggestion" onClick={() => createSessionAndSend('Quelle est la frequentation de la gare Paris Gare de Lyon en 2024 ?')}>
                Quelle est la frequentation de la gare Paris Gare de Lyon en 2024 ?
              </button>
              <button className="suggestion" onClick={() => createSessionAndSend('Quel est le taux de proprete de la gare de Bordeaux Saint-Jean ?')}>
                Quel est le taux de proprete de la gare de Bordeaux Saint-Jean ?
              </button>
              <button className="suggestion" onClick={() => createSessionAndSend('Quels equipements PMR sont disponibles en gare ?')}>
                Quels equipements PMR sont disponibles en gare ?
              </button>
            </div>
            <button className="btn-create" onClick={createSession}>
              Nouvelle recherche
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
