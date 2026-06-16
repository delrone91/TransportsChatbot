import { useState } from 'react'
import './Sidebar.css'

// Barre latérale avec la liste des conversations et les infos utilisateur
export default function Sidebar({ sessions, activeSession, user, onSelect, onCreate, onDelete, onLogout }) {
  const [hovered, setHovered] = useState(null) // conversation survolée (pour afficher le bouton supprimer)

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <div className="sidebar-brand">🚆 TransportBot</div>
        {/* Bouton pour créer une nouvelle conversation */}
        <button className="btn-new" onClick={onCreate} title="Nouvelle conversation">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </button>
      </div>

      {/* Liste des conversations existantes */}
      <nav className="sessions-list">
        {sessions.length === 0 && (
          <p className="no-sessions">Aucune conversation.<br />Cliquez sur + pour commencer.</p>
        )}
        {sessions.map(session => (
          <div
            key={session.id}
            className={`session-item ${activeSession?.id === session.id ? 'active' : ''}`}
            onClick={() => onSelect(session)}
            onMouseEnter={() => setHovered(session.id)}
            onMouseLeave={() => setHovered(null)}
          >
            <span className="session-icon">💬</span>
            <span className="session-title">{session.title}</span>
            {/* Bouton supprimer visible uniquement au survol */}
            {hovered === session.id && (
              <button
                className="btn-del"
                onClick={(e) => onDelete(session.id, e)}
                title="Supprimer"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        ))}
      </nav>

      {/* Pied de sidebar : avatar, nom et bouton de déconnexion */}
      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">{user?.username?.[0]?.toUpperCase()}</div>
          <span className="user-name">{user?.username}</span>
        </div>
        <button className="btn-logout" onClick={onLogout} title="Se déconnecter">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </aside>
  )
}
