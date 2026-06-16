import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import './ChatWindow.css'

// Zone principale qui affiche tous les messages d'une conversation
export default function ChatWindow({ messages, sending }) {
  const bottomRef = useRef(null)

  // À chaque nouveau message, on fait défiler jusqu'en bas automatiquement
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  return (
    <div className="chat-window">
      {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}

      {/* Indicateur de chargement (3 points animés) pendant que le bot répond */}
      {sending && (
        <div className="message assistant">
          <div className="bubble typing">
            <span /><span /><span />
          </div>
        </div>
      )}

      {/* Élément invisible en bas de page, utilisé comme cible pour le scroll automatique */}
      <div ref={bottomRef} />
    </div>
  )
}
