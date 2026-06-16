import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import MessageInput from '../components/MessageInput'
import './ChatPage.css'

export default function ChatPage() {
  const { user, logout } = useAuth()
  const [sessions, setSessions] = useState([])        // liste de toutes les conversations
  const [activeSession, setActiveSession] = useState(null)  // conversation actuellement ouverte
  const [messages, setMessages] = useState([])         // messages de la conversation active
  const [sending, setSending] = useState(false)        // true pendant qu'on attend la réponse du bot

  // On charge les conversations dès que la page s'affiche
  useEffect(() => { fetchSessions() }, [])

  const fetchSessions = async () => {
    try {
      const r = await client.get('/chat/sessions')
      setSessions(r.data)
    } catch {}
  }

  // Crée une nouvelle conversation vide
  const createSession = async () => {
    const r = await client.post('/chat/sessions', {})
    setSessions(prev => [r.data, ...prev])
    setActiveSession(r.data)
    setMessages([])
  }

  // Change de conversation et charge ses messages
  const selectSession = async (session) => {
    if (activeSession?.id === session.id) return
    setActiveSession(session)
    setMessages([])
    const r = await client.get(`/chat/sessions/${session.id}`)
    setMessages(r.data.messages)
  }

  // Supprime une conversation (le bouton × qui apparaît au survol)
  const deleteSession = async (sessionId, e) => {
    e.stopPropagation() // évite de sélectionner la session en même temps
    await client.delete(`/chat/sessions/${sessionId}`)
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (activeSession?.id === sessionId) {
      setActiveSession(null)
      setMessages([])
    }
  }

  // Envoie un message dans une session donnée et attend la réponse du bot
  const sendMessageToSession = async (session, content) => {
    const tempId = Date.now()
    // On affiche le message utilisateur immédiatement (sans attendre le serveur)
    setMessages(prev => [...prev, { id: tempId, role: 'user', content }])
    setSending(true)
    try {
      const r = await client.post(`/chat/sessions/${session.id}/messages`, { content })
      // On remplace le message temporaire par les vrais messages retournés par le backend
      setMessages(prev => [
        ...prev.filter(m => m.id !== tempId),
        r.data.user_message,
        r.data.assistant_message,
      ])
      // Le titre de la conversation est mis à jour avec le premier message
      const newTitle = r.data.session_title
      setSessions(prev => prev.map(s => s.id === session.id ? { ...s, title: newTitle } : s))
      setActiveSession(prev => ({ ...prev, title: newTitle }))
    } catch {
      // En cas d'erreur, on supprime le message temporaire
      setMessages(prev => prev.filter(m => m.id !== tempId))
    } finally {
      setSending(false)
    }
  }

  // Utilisé par le champ de saisie (conversation déjà ouverte)
  const sendMessage = async (content) => {
    if (!activeSession || sending) return
    await sendMessageToSession(activeSession, content)
  }

  // Utilisé par les boutons de suggestion : crée une session ET envoie le message directement
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
          // Page d'accueil affichée quand aucune conversation n'est sélectionnée
          <div className="chat-empty">
            <div className="empty-icon">🚆</div>
            <h2>TransportBot</h2>
            <p>Votre assistant pour les transports en commun français</p>
            <div className="empty-suggestions">
              <p className="suggestions-label">Exemples de questions :</p>
              <button className="suggestion" onClick={() => createSessionAndSend('Quel est le prix du forfait Navigo mensuel ?')}>
                Quel est le prix du forfait Navigo mensuel ?
              </button>
              <button className="suggestion" onClick={() => createSessionAndSend('Quels équipements pour les personnes handicapées en gare ?')}>
                Quels équipements pour les personnes handicapées en gare ?
              </button>
              <button className="suggestion" onClick={() => createSessionAndSend('Comment fonctionne le Navigo Liberté+ ?')}>
                Comment fonctionne le Navigo Liberté+ ?
              </button>
            </div>
            <button className="btn-create" onClick={createSession}>
              + Nouvelle conversation
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
