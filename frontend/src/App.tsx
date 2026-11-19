import { FormEvent, useEffect, useState } from 'react'

type Message = { role: 'assistant' | 'user'; content: string; sources?: { filename: string; excerpt: string }[] }
type Project = {
  name: string
  full_name: string
  description: string
  html_url: string
  language: string | null
  updated_at: string
  topics: string[]
}

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const copy = {
  en: {
    eyebrow: 'PERSONAL CAREER ASSISTANT',
    title: 'Get to know',
    name: 'Rafed Zidi.',
    intro: 'Explore my background, projects and technical skills. Ask my AI assistant a question in English or French.',
    role: 'Data Science · Business Intelligence · Software Development',
    about: 'A profile built around data',
    aboutText: 'I am a Business Computing graduate specializing in Business Intelligence, currently pursuing a Professional Master’s in Data Science and Software Development at ESEN.',
    projects: 'Selected projects',
    projectsLoading: 'Loading public GitHub projects…',
    projectsEmpty: 'No public repositories with the “portfolio” topic were found. Add this topic to repositories you want to show.',
    projectsError: 'GitHub projects could not be loaded. Please try again later.',
    projectsRetry: 'Retry',
    noDescription: 'No project description provided.',
    repository: 'GitHub repository',
    skills: 'Tools & technologies',
    chatTitle: 'Ask Rafed AI',
    chatSub: 'Ask about skills, education or projects',
    placeholder: 'Ask a question about Rafed…',
    send: 'Send',
    welcome: 'Hello! I can answer questions about Rafed’s education, skills and projects. What would you like to know?',
    suggestions: ['Present Rafed’s profile', 'Tell me about the SCB project', 'Which BI tools does he use?'],
    source: 'Sources',
    error: 'I could not reach the assistant. Make sure the FastAPI backend is running.',
    footer: 'Built as a personal AI portfolio project.'
  },
  fr: {
    eyebrow: 'ASSISTANT CARRIÈRE PERSONNEL',
    title: 'Découvrez',
    name: 'Rafed Zidi.',
    intro: 'Explorez mon parcours, mes projets et mes compétences techniques. Posez une question à mon assistant IA en français ou en anglais.',
    role: 'Data Science · Business Intelligence · Développement logiciel',
    about: 'Un parcours orienté data',
    aboutText: 'Je suis diplômé en Informatique de Gestion, spécialité Business Intelligence, et je poursuis actuellement un Mastère Professionnel en Data Science and Software Development à l’ESEN.',
    projects: 'Projets sélectionnés',
    projectsLoading: 'Chargement des projets GitHub publics…',
    projectsEmpty: 'Aucun dépôt public avec le topic « portfolio » trouvé. Ajoutez ce topic aux dépôts que vous souhaitez afficher.',
    projectsError: 'Impossible de charger les projets GitHub. Veuillez réessayer plus tard.',
    projectsRetry: 'Réessayer',
    noDescription: 'Aucune description du projet disponible.',
    repository: 'Dépôt GitHub',
    skills: 'Outils & technologies',
    chatTitle: 'Demander à Rafed AI',
    chatSub: 'Questions sur les compétences, les études ou les projets',
    placeholder: 'Posez une question sur Rafed…',
    send: 'Envoyer',
    welcome: 'Bonjour ! Je peux répondre à vos questions sur les études, les compétences et les projets de Rafed. Que souhaitez-vous savoir ?',
    suggestions: ['Présente le profil de Rafed', 'Parle-moi du projet SCB', 'Quels outils BI maîtrise-t-il ?'],
    source: 'Sources',
    error: 'Impossible de joindre l’assistant. Vérifiez que le backend FastAPI est lancé.',
    footer: 'Réalisé comme projet de portfolio IA personnel.'
  }
}

export default function App() {
  const [language, setLanguage] = useState<'en' | 'fr'>('en')
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [projectsLoading, setProjectsLoading] = useState(true)
  const [projectsError, setProjectsError] = useState(false)
  const [projectsRetry, setProjectsRetry] = useState(0)
  const t = copy[language]

  useEffect(() => {
    let active = true

    async function loadProjects() {
      const retryDelays = [2000, 5000, 10000]
      for (let attempt = 0; attempt <= retryDelays.length; attempt += 1) {
        if (!active) return
        try {
          const response = await fetch(`${API_URL}/api/projects`)
          if (!response.ok) throw new Error('GitHub project request failed')
          const data: Project[] = await response.json()
          if (active) {
            setProjects(data)
            setProjectsError(false)
          }
          return
        } catch {
          if (attempt === retryDelays.length) {
            if (active) setProjectsError(true)
            return
          }
          await new Promise((resolve) => window.setTimeout(resolve, retryDelays[attempt]))
        }
      }
    }

    async function loadProjectsAndFinish() {
      try {
        await loadProjects()
      } finally {
        if (active) setProjectsLoading(false)
      }
    }

    void loadProjectsAndFinish()
    return () => {
      active = false
    }
  }, [projectsRetry])

  function retryProjects() {
    setProjectsError(false)
    setProjectsLoading(true)
    setProjectsRetry((attempt) => attempt + 1)
  }

  async function sendMessage(event?: FormEvent, suggested?: string) {
    event?.preventDefault()
    const message = (suggested ?? input).trim()
    if (!message || loading) return

    setMessages((current) => [...current, { role: 'user', content: message }])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, language }),
      })
      if (!response.ok) throw new Error('API request failed')
      const data = await response.json()
      setMessages((current) => [...current, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources ?? [],
      }])
    } catch {
      setMessages((current) => [...current, { role: 'assistant', content: t.error }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="site-shell">
      <nav className="topbar">
        <a className="brand" href="#home"><span className="brand-mark">R.</span><span>RAFED ZIDI</span></a>
        <div className="nav-links">
          <a href="#about">{language === 'en' ? 'About' : 'À propos'}</a>
          <a href="#projects">{language === 'en' ? 'Projects' : 'Projets'}</a>
          <a href="#assistant">{language === 'en' ? 'AI Assistant' : 'Assistant IA'}</a>
        </div>
        <div className="nav-actions">
          <button className="language-toggle" onClick={() => setLanguage(language === 'en' ? 'fr' : 'en')}>
            {language === 'en' ? 'FR' : 'EN'} <span>↗</span>
          </button>
          <a className="contact-link" href="https://www.linkedin.com/" target="_blank" rel="noreferrer">LinkedIn ↗</a>
        </div>
      </nav>

      <section className="hero" id="home">
        <div className="hero-copy">
          <div className="eyebrow"><span className="status-dot" />{t.eyebrow}</div>
          <h1>{t.title}<br /><span>{t.name}</span></h1>
          <p className="hero-role">{t.role}</p>
          <p className="hero-intro">{t.intro}</p>
          <div className="hero-buttons">
            <a className="primary-button" href="#assistant">{language === 'en' ? 'Talk to my AI assistant' : 'Parler à mon assistant IA'} <span>↗</span></a>
            <a className="secondary-button" href="https://github.com/rafazidi" target="_blank" rel="noreferrer">GitHub ↗</a>
          </div>
        </div>
        <div className="hero-visual">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="profile-card">
            <div className="profile-initials">RZ</div>
            <div className="profile-card-bottom"><span>DATA & INTELLIGENCE</span><span>TN · 2026</span></div>
          </div>
          <div className="floating-note note-top"><span className="note-icon">✳</span> Curious by design</div>
          <div className="floating-note note-bottom"><span className="status-dot" /> AI assistant available</div>
        </div>
      </section>

      <section className="about-section section-grid" id="about">
        <div className="section-label">01 / {language === 'en' ? 'PROFILE' : 'PROFIL'}</div>
        <div className="section-content">
          <h2>{t.about}</h2>
          <p className="large-copy">{t.aboutText}</p>
          <div className="stats-row">
            <div><strong>BI</strong><span>Business Intelligence</span></div>
            <div><strong>AI</strong><span>Data & intelligent systems</span></div>
            <div><strong>FR / EN</strong><span>Communication</span></div>
          </div>
        </div>
      </section>

      <section className="projects-section section-grid" id="projects">
        <div className="section-label">02 / {t.projects.toUpperCase()}</div>
        <div className="section-content">
          <h2>{t.projects}</h2>
          <div className="project-list">
            {projectsLoading && <p className="project-status">{t.projectsLoading}</p>}
            {projectsError && <p className="project-status" role="alert">{t.projectsError} <button type="button" onClick={retryProjects}>{t.projectsRetry}</button></p>}
            {!projectsLoading && !projectsError && projects.length === 0 && <p className="project-status">{t.projectsEmpty}</p>}
            {projects.map((project, index) => (
              <article className="project-card" key={project.full_name}>
                <div className="project-number">{String(index + 1).padStart(2, '0')}</div>
                <div>
                  <h3>{project.name}</h3>
                  <p>{project.description || t.noDescription}</p>
                  {project.language && <span className="project-language">{project.language}</span>}
                  <a href={project.html_url} target="_blank" rel="noreferrer">{t.repository} ↗</a>
                </div>
                <span className="project-arrow">↗</span>
              </article>
            ))}
          </div>
          <h3 className="skills-heading">{t.skills}</h3>
          <div className="skill-tags">{['Python', 'SQL', 'Power BI', 'SSIS', 'SSAS', 'Data Warehousing', 'Talend', 'Oracle PL/SQL', 'MongoDB', 'R', 'GitHub'].map((skill) => <span key={skill}>{skill}</span>)}</div>
        </div>
      </section>

      <section className="assistant-section section-grid" id="assistant">
        <div className="section-label">03 / AI ASSISTANT</div>
        <div className="section-content assistant-layout">
          <div className="assistant-heading">
            <div className="eyebrow"><span className="status-dot" /> RAG-POWERED PROFILE</div>
            <h2>{t.chatTitle}</h2>
            <p>{t.chatSub}</p>
            <div className="suggestions">
              {t.suggestions.map((suggestion) => <button key={suggestion} onClick={() => sendMessage(undefined, suggestion)}>{suggestion} <span>↗</span></button>)}
            </div>
          </div>
          <div className="chat-window">
            <div className="chat-header"><div className="bot-avatar">R.</div><div><strong>Rafed AI</strong><span><i /> {language === 'en' ? 'Career assistant' : 'Assistant professionnel'}</span></div><span className="chat-language">{language.toUpperCase()}</span></div>
            <div className="chat-messages">
              {messages.length === 0 && <div className="message assistant-message">{t.welcome}</div>}
              {messages.map((message, index) => <div key={index} className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}>
                {message.content}
                {message.sources && message.sources.length > 0 && <div className="sources"><strong>{t.source}</strong>{message.sources.map((source, i) => <div key={i}><span>{source.filename}</span><small>{source.excerpt}</small></div>)}</div>}
              </div>)}
              {loading && <div className="message assistant-message typing">Rafed AI is thinking<span> · · ·</span></div>}
            </div>
            <form className="chat-input" onSubmit={(event) => sendMessage(event)}>
              <input value={input} onChange={(event) => setInput(event.target.value)} placeholder={t.placeholder} aria-label={t.placeholder} />
              <button type="submit" disabled={loading || !input.trim()}>{t.send} <span>↗</span></button>
            </form>
            <div className="chat-disclaimer">AI-generated answers based on the profile documents. Please verify important details.</div>
          </div>
        </div>
      </section>

      <footer><a className="brand" href="#home"><span className="brand-mark">R.</span><span>RAFED ZIDI</span></a><span>{t.footer}</span><a href="#home">Back to top ↑</a></footer>
    </main>
  )
}
