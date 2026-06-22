import { useState, useRef, useEffect } from 'react'
import './MessageInput.css'

export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const [useWeb, setUseWeb] = useState(false)
  const [listening, setListening] = useState(false)
  const textareaRef = useRef(null)
  const recognitionRef = useRef(null)

  const voiceSupported = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  useEffect(() => {
    return () => recognitionRef.current?.stop()
  }, [])

  const toggleVoice = () => {
    if (listening) {
      recognitionRef.current?.stop()
      return
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const rec = new SR()
    rec.lang = 'fr-FR'
    rec.continuous = false
    rec.interimResults = false

    rec.onstart = () => setListening(true)
    rec.onend = () => setListening(false)
    rec.onerror = () => setListening(false)

    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      setValue(prev => (prev ? prev + ' ' + transcript : transcript))
      textareaRef.current?.focus()
    }

    recognitionRef.current = rec
    rec.start()
  }

  const submit = () => {
    if (!value.trim() || disabled) return
    onSend(value.trim(), useWeb)
    setValue('')
    textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const handleInput = (e) => {
    setValue(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
  }

  return (
    <div className="input-bar">
      <div className={`input-wrapper ${useWeb ? 'input-wrapper--web' : ''}`}>
        <button
          className={`web-toggle ${useWeb ? 'web-toggle--active' : ''}`}
          onClick={() => setUseWeb(v => !v)}
          title={useWeb ? 'Recherche web activee' : 'Activer la recherche web'}
          type="button"
        >
          Web
        </button>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={useWeb ? 'Chercher une information recente...' : 'Demandez un tarif, une gare, un equipement...'}
          disabled={disabled}
          rows={1}
        />
        {voiceSupported && (
          <button
            className={`mic-btn ${listening ? 'mic-btn--active' : ''}`}
            onClick={toggleVoice}
            type="button"
            title={listening ? "Arreter l'ecoute" : 'Dicter la question'}
          >
            {listening ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12" rx="2"/>
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2H3v2a9 9 0 0 0 8 8.94V22H8v2h8v-2h-3v-1.06A9 9 0 0 0 21 12v-2h-2z"/>
              </svg>
            )}
          </button>
        )}
        <button onClick={submit} disabled={disabled || !value.trim()} className="send-btn" title="Envoyer">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
      <p className={useWeb ? 'web-hint' : 'input-hint'}>
        {useWeb ? 'Recherche sur des sources en ligne fiables.' : 'Entree pour envoyer, Shift + Entree pour aller a la ligne.'}
      </p>
    </div>
  )
}
