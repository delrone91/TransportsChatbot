import ReactMarkdown from 'react-markdown'

// Affiche un message sous forme de bulle (gauche = bot, droite = utilisateur)
export default function MessageBubble({ message }) {
  return (
    <div className={`message ${message.role}`}>
      <div className="bubble">
        {/* Les réponses du bot sont en Markdown, on les transforme en HTML */}
        {message.role === 'assistant'
          ? <ReactMarkdown>{message.content}</ReactMarkdown>
          : message.content}
      </div>
    </div>
  )
}
