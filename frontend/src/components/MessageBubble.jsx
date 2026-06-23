import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './MessageBubble.css'

const SOURCE_LABELS = {
  rag: { label: 'Donnees locales' },
  web: { label: 'Web verifie' },
}

// Libelles lisibles pour les jeux de donnees locaux (RAG)
const RAG_SOURCE_LABELS = {
  tarif: 'Tarifs Ile-de-France Mobilites',
  horaire: 'Horaires des gares SNCF',
  freq: 'Frequentation des gares SNCF',
  equip: 'Equipements accessibilite SNCF',
  proprete: 'Proprete en gare SNCF',
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

  const ragLabels = message.role === 'assistant' && message.rag_sources?.length > 0
    ? [...new Set(message.rag_sources.map((src) => RAG_SOURCE_LABELS[src.type] || src.source))]
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
              key={s.url || i}
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

      {ragLabels.length > 0 && (
        <div className="rag-sources">
          {ragLabels.map((label) => (
            <span key={label} className="rag-source-chip">{label}</span>
          ))}
        </div>
      )}
    </div>
  )
}
