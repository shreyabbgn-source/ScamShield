const API = 'http://127.0.0.1:8000/api'

const RISK = {
  LOW:      { cls: 'risk-low',  label: 'LOW RISK',      emoji: '✅' },
  MEDIUM:   { cls: 'risk-med',  label: 'MEDIUM RISK',   emoji: '⚠️' },
  HIGH:     { cls: 'risk-high', label: 'HIGH RISK',     emoji: '🚨' },
  CRITICAL: { cls: 'risk-crit', label: 'CRITICAL RISK', emoji: '☠️' },
}

const LAYER_COLORS = ['#6366f1','#8b5cf6','#ec4899','#06b6d4']

const ACTIONS = {
  banking_scam:    ['Do not click any links', 'Verify via official bank app', 'Report to bank + CERT-In'],
  investment_scam: ['Do not send money', 'Verify on SEBI website', 'Report to cybercrime.gov.in'],
  phishing_scam:   ['Do not enter credentials', 'Report URL to Google', 'Enable 2FA immediately'],
  job_scam:        ['Never pay registration fee', 'Verify company on LinkedIn', 'Report to cybercrime.gov.in'],
  lottery_scam:    ['Cannot win unregistered lottery', 'Do not pay any fee', 'Delete and block'],
  task_scam:       ['Never pay advance deposits', 'Report the group', 'Report to cybercrime.gov.in'],
  unknown:         ['Exercise caution', 'Do not share personal info', 'Verify before acting'],
}

function getActions(category) {
  const key = Object.keys(ACTIONS).find(k => category?.includes(k)) || 'unknown'
  return ACTIONS[key]
}

// CSS color for a risk class
function riskColor(cls) {
  return { 'risk-low':'#22c55e','risk-med':'#f59e0b','risk-high':'#ef4444','risk-crit':'#dc2626' }[cls] || '#f59e0b'
}

let pageData = null

// Simple element builder — NO style.cssText, only className
function mk(tag, className, text) {
  const n = document.createElement(tag)
  if (className) n.className = className
  if (text !== undefined) n.textContent = text
  return n
}

async function init() {
  const app = document.getElementById('app')
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const posts = []
        document.querySelectorAll('article').forEach((article, index) => {
          let caption = ''
          article.querySelectorAll('span, h1, div').forEach(el => {
            const t = el.innerText?.trim()
            if (t && t.length > 15 && t.length < 800 && !caption && el.children.length === 0) caption = t
          })
          let imageUrl = ''
          const img = article.querySelector('img')
          if (img) imageUrl = img.srcset?.split(',')[0]?.split(' ')[0] || img.src
          let username = ''
          const userEl = article.querySelector('header a, a[href*="/"] span')
          if (userEl) username = userEl.innerText?.trim()
          if (caption || imageUrl) posts.push({ index, caption: caption.slice(0,400), imageUrl, username: username||'Unknown', preview: caption.slice(0,70)||'Image post' })
        })
        if (posts.length === 0) {
          const texts = []
          document.querySelectorAll('p,h1,h2,h3,span,li').forEach(el => {
            if (el.children.length === 0) { const t = el.innerText?.trim(); if (t && t.length>25 && t.length<500) texts.push(t) }
          })
          const imgs = [...document.querySelectorAll('img')].filter(i=>i.width>80&&i.src?.startsWith('http')).map(i=>i.src)
          if (texts.length>0) posts.push({ index:0, caption:[...new Set(texts)].slice(0,4).join(' ').slice(0,500), imageUrl:imgs[0]||'', username:window.location.hostname, preview:texts[0].slice(0,70) })
        }
        return { platform: window.location.hostname.includes('instagram')?'instagram':window.location.hostname.includes('whatsapp')?'whatsapp':'webpage', posts:posts.slice(0,6), pageUrl:window.location.href, pageTitle:document.title }
      }
    })
    pageData = results[0].result
  } catch(e) {
    pageData = { platform:'webpage', posts:[], pageUrl:tab.url, pageTitle:tab.title }
  }
  renderPostList(app)
}

function renderPostList(app) {
  app.innerHTML = ''
  const { platform, posts, pageTitle } = pageData
  const platformEmoji = {instagram:'📸',whatsapp:'💬',webpage:'🌐'}[platform]||'🌐'

  if (posts.length === 0) {
    const wrap = mk('div','empty-wrap')
    wrap.appendChild(mk('div','empty-icon','🔍'))
    wrap.appendChild(mk('p','empty-title','No posts detected on this page.'))
    wrap.appendChild(mk('p','empty-sub','Try opening a specific post or paste text below.'))
    const ta = mk('textarea','empty-textarea')
    ta.placeholder = 'Paste text to scan manually...'
    ta.rows = 3
    const btn = mk('button','empty-btn','🔍 Scan Text')
    btn.addEventListener('click', () => { const t = ta.value.trim(); if(t) runScan(t) })
    wrap.appendChild(ta)
    wrap.appendChild(btn)
    app.appendChild(wrap)
    return
  }

  const hdr = mk('div','plat-header')
  hdr.appendChild(mk('span','plat-label', `${platformEmoji} ${platform.toUpperCase()} · ${posts.length} post${posts.length>1?'s':''} detected`))
  hdr.appendChild(mk('span','plat-title', (pageTitle||'').slice(0,30)))
  app.appendChild(hdr)

  posts.forEach((post, i) => {
    const card = mk('div','post-card')
    card.addEventListener('click', () => selectPost(i))

    if (post.imageUrl) {
      const img = document.createElement('img')
      img.className = 'post-thumb'
      img.src = post.imageUrl
      img.addEventListener('error', () => { img.style.display='none' })
      card.appendChild(img)
    } else {
      const ph = mk('div','post-thumb-placeholder', platform==='instagram'?'📸':'💬')
      card.appendChild(ph)
    }

    const info = mk('div','post-info')
    info.appendChild(mk('div','post-user', post.username!=='Unknown'?'@'+post.username:`${platform.toUpperCase()} · Post ${i+1}`))
    info.appendChild(mk('div','post-preview', post.preview||'Image post'))
    card.appendChild(info)
    card.appendChild(mk('div','post-arrow','›'))
    app.appendChild(card)
  })

  const manual = mk('div','manual-wrap')
  manual.appendChild(mk('p','manual-label','Or scan custom text:'))
  const row = mk('div','manual-row')
  const ta = mk('textarea','manual-textarea')
  ta.placeholder = 'Paste any text...'
  ta.rows = 2
  const btn = mk('button','manual-btn','Scan ›')
  btn.addEventListener('click', () => { const t = ta.value.trim(); if(t) runScan(t) })
  row.appendChild(ta)
  row.appendChild(btn)
  manual.appendChild(row)
  app.appendChild(manual)
}

function selectPost(i) {
  const post = pageData.posts[i]
  if (post) runScan(post.caption)
}

async function runScan(caption) {
  const app = document.getElementById('app')
  app.innerHTML = ''

  const wrap = mk('div','scan-wrap')
  wrap.appendChild(mk('div','scan-icon','🔍'))
  wrap.appendChild(mk('p','scan-title','Analyzing with 4-layer AI...'))
  wrap.appendChild(mk('p','scan-sub','Pattern · ML · BERT · Transformer'))
  const barWrap = mk('div','scan-bar-wrap')
  const bar = mk('div','scan-bar')
  barWrap.appendChild(bar)
  wrap.appendChild(barWrap)
  app.appendChild(wrap)

  let prog = 0
  const ticker = setInterval(() => { prog = Math.min(85, prog + Math.random()*12); bar.style.width = prog+'%' }, 200)

  try {
    const fd = new FormData()
    fd.append('caption', caption)
    const res = await fetch(`${API}/scan`, { method:'POST', body:fd })
    clearInterval(ticker)
    bar.style.width = '100%'
    if (!res.ok) throw new Error(res.status)
    renderResult(app, await res.json())
  } catch(err) {
    clearInterval(ticker)
    app.innerHTML = ''
    const box = mk('div','err-box')
    box.appendChild(mk('p','err-title','⚠ Cannot connect to backend'))
    box.appendChild(mk('p','err-sub','Make sure the server is running:'))
    box.appendChild(mk('code','err-code','uvicorn main:app --reload'))
    const btn = mk('button','retry-btn','← Try Again')
    btn.addEventListener('click', () => location.reload())
    app.appendChild(box)
    app.appendChild(btn)
  }
}

function renderResult(app, data) {
  app.innerHTML = ''
  const risk = RISK[data.risk] || RISK.MEDIUM
  const color = riskColor(risk.cls)
  const pct = Math.round(data.scam_probability * 100)
  const actions = getActions(data.category)

  const layerMatch = data.explanation?.match(/Pattern:\s*(\d+)%.*ML:\s*(\d+)%.*BERT:\s*(\d+)%.*Transformer:\s*(\d+)%/)
  const layers = layerMatch
    ? [['Pattern',layerMatch[1]],['ML',layerMatch[2]],['BERT',layerMatch[3]],['Transformer',layerMatch[4]]].map(([name,score],i) => ({name, score:parseInt(score), color:LAYER_COLORS[i]}))
    : []

  const card = mk('div','result-card')
  card.style.borderColor = color + '40'  // only border-color, not a handler

  // Risk row
  const riskRow = mk('div','risk-row')
  const riskLeft = mk('div')
  const badge = mk('div', `risk-badge ${risk.cls}`, `${risk.emoji} ${risk.label}`)
  const br = document.createElement('br')
  const catBadge = mk('div','cat-badge', data.category.replace(/_/g,' '))
  riskLeft.appendChild(badge); riskLeft.appendChild(br); riskLeft.appendChild(catBadge)
  const circle = mk('div','score-circle', `${pct}%`)
  circle.style.borderColor = color
  circle.style.color = color
  riskRow.appendChild(riskLeft); riskRow.appendChild(circle)
  card.appendChild(riskRow)

  // Progress
  const pb = mk('div','progress-wrap')
  const pf = mk('div','progress-fill')
  pf.style.width = pct+'%'; pf.style.background = color
  pb.appendChild(pf); card.appendChild(pb)

  // Layers
  if (layers.length) {
    const sec = mk('div','section')
    sec.appendChild(mk('p','section-label','Confidence Breakdown'))
    layers.forEach(l => {
      const row = mk('div','layer-row')
      row.appendChild(mk('span','layer-name',l.name))
      const track = mk('div','layer-track')
      const fill = mk('div','layer-fill')
      fill.style.width = l.score+'%'; fill.style.background = l.color
      track.appendChild(fill); row.appendChild(track)
      const pctEl = mk('span','layer-pct',l.score+'%')
      pctEl.style.color = l.color
      row.appendChild(pctEl)
      sec.appendChild(row)
    })
    card.appendChild(sec)
  }

  // Evidence
  const evidence = data.weighted_evidence || []
  if (evidence.length) {
    const sec = mk('div','section')
    sec.appendChild(mk('p','section-label','Evidence Detected'))
    evidence.slice(0,3).forEach(e => {
      const text = typeof e==='object'?e.text:e
      const weight = typeof e==='object'?e.weight:10
      const row = mk('div','ev-row')
      const evText = mk('span','ev-text', '⚠ '+text.slice(0,32))
      evText.style.color = color
      const track = mk('div','ev-track')
      const fill = mk('div','ev-fill')
      fill.style.width = Math.min(100,weight*3)+'%'; fill.style.background = color
      track.appendChild(fill)
      row.appendChild(evText); row.appendChild(track)
      row.appendChild(mk('span','ev-pct',weight+'%'))
      sec.appendChild(row)
    })
    card.appendChild(sec)
  }

  // Actions
  const actSec = mk('div')
  actSec.appendChild(mk('p','section-label-green','🛡 Recommended Actions'))
  actions.forEach((a,i) => {
    const row = mk('div','act-row')
    row.appendChild(mk('span','act-num',`${i+1}.`))
    row.appendChild(mk('span','act-text',a))
    actSec.appendChild(row)
  })
  card.appendChild(actSec)
  app.appendChild(card)

  const dashBtn = mk('button','dash-btn','Open Full Dashboard ↗')
  dashBtn.addEventListener('click', () => chrome.tabs.create({url:'http://localhost:5173'}))
  app.appendChild(dashBtn)

  const backBtn = mk('button','back-btn','← Back to Posts')
  backBtn.addEventListener('click', () => renderPostList(document.getElementById('app')))
  app.appendChild(backBtn)
}

init()