import { useState, useRef } from 'react'
import './MessageInput.css'

// Champ de saisie du message avec envoi par Entrée et redimensionnement automatique
export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  const submit = () => {
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
    textareaRef.current.style.height = 'auto' // remet la hauteur à la normale après envoi
  }

  const handleKeyDown = (e) => {
    // Entrée seule = envoyer, Shift+Entrée = saut de ligne
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const handleInput = (e) => {
    setValue(e.target.value)
    // On ajuste la hauteur du textarea en fonction du contenu (max 160px)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
  }

  return (
    <div className="input-bar">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Posez votre question sur les transports... (Entrée pour envoyer)"
          disabled={disabled}
          rows={1}
        />
        <button onClick={submit} disabled={disabled || !value.trim()} className="send-btn" title="Envoyer">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
      <p className="input-hint">Shift+Entrée pour sauter une ligne</p>
    </div>
  )
}
