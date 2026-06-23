import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './MessageBubble.css'

const SOURCE_LABELS = {
  rag: { label: 'Données locales' },
  web: { label: 'Web vérifié' },
}

// Jeux de donnees locaux (RAG) : libelle + page open data officielle
const RAG_SOURCES = {
  tarif:    { label: 'Tarifs Île-de-France Mobilités', url: 'https://data.iledefrance-mobilites.fr/explore/dataset/titres-et-tarifs/information/' },
  horaire:  { label: 'Horaires des gares SNCF', url: 'https://ressources.data.sncf.com/explore/dataset/horaires-des-gares1/information/' },
  freq:     { label: 'Fréquentation des gares SNCF', url: 'https://ressources.data.sncf.com/explore/dataset/frequentation-gares/information/' },
  equip:    { label: 'Équipements accessibilité SNCF', url: 'https://ressources.data.sncf.com/explore/dataset/equipements-accessibilite-sncf/information/' },
  proprete: { label: 'Propreté en gare SNCF', url: 'https://ressources.data.sncf.com/explore/dataset/proprete-en-gare/information/' },
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
    ? [...new Map(
        message.rag_sources
          .map((src) => RAG_SOURCES[src.type])
          .filter(Boolean)
          .map((s) => [s.url, s])
      ).values()]
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
          <span className="web-sources-label">Sources consultées</span>
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

      {ragSources.length > 0 && (
        <div className="rag-sources">
          {ragSources.map((s) => (
            <a
              key={s.url}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="rag-source-chip"
            >
              {s.label}
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
