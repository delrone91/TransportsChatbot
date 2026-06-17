import ReactMarkdown from 'react-markdown'
import './MessageBubble.css'

const SOURCE_LABELS = {
  rag: { icon: '📊', label: 'Données SNCF/IDFM' },
  web: { icon: '🌐', label: 'Source web' },
}

export default function MessageBubble({ message }) {
  const badge = message.role === 'assistant' && message.source
    ? SOURCE_LABELS[message.source]
    : null

  const webSources = message.role === 'assistant' && message.web_sources?.length > 0
    ? message.web_sources
    : []

  return (
    <div className={`message ${message.role}`}>
      <div className="bubble">
        {message.role === 'assistant'
          ? <ReactMarkdown>{message.content}</ReactMarkdown>
          : message.content}
      </div>

      {badge && webSources.length === 0 && (
        <div className={`source-badge source-badge--${message.source}`}>
          {badge.icon} {badge.label}
        </div>
      )}

      {webSources.length > 0 && (
        <div className="web-sources">
          <span className="web-sources-label">🌐 Sources :</span>
          {webSources.map((s, i) => (
            <a
              key={i}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="web-source-link"
            >
              {s.title}
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
