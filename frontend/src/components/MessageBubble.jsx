import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './MessageBubble.css'

const SOURCE_LABELS = {
  rag: { label: 'Donnees locales' },
  web: { label: 'Web verifie' },
}

function normalizeMarkdown(content = '') {
  return content
    .replace(/\|\s+\|(?=\s*[-\wÀ-ÿ])/g, '|\n|')
    .replace(/(\|[\s:-]+\|)\s+\|/g, '$1\n|')
}

export default function MessageBubble({ message }) {
  const badge = message.role === 'assistant' && message.source
    ? SOURCE_LABELS[message.source]
    : null

  const webSources = message.role === 'assistant' && message.web_sources?.length > 0
    ? message.web_sources
    : []

  const ragSources = message.role === 'assistant' && message.rag_sources?.length > 0
    ? Array.from(
        new Map(
          message.rag_sources.map((src) => [`${src.source}-${src.type}`, src])
        ).values()
      )
    : []

  const renderedContent = normalizeMarkdown(message.content)

  return (
    <div className={`message ${message.role}`}>
      <div className="bubble">
        {message.role === 'assistant'
          ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{renderedContent}</ReactMarkdown>
          : message.content}
      </div>

      {badge && webSources.length === 0 && (
        <div className={`source-badge source-badge--${message.source}`}>
          {badge.label}
        </div>
      )}

      {webSources.length > 0 && (
        <div className="web-sources">
          <span className="web-sources-label">Sources consultees</span>
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

      {ragSources.length > 0 && (
        <div className="sources">
          {ragSources.map((src, index) => (
            <div key={index}>
              {src.source} - {src.type}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
