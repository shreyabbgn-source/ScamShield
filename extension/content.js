function extractInstagramPosts() {
  const posts = []

  // Instagram post articles
  const articles = document.querySelectorAll('article')

  articles.forEach((article, index) => {
    // Caption text
    let caption = ''
    const captionEls = article.querySelectorAll('h1, span, ._a9zs, [data-testid] span')
    captionEls.forEach(el => {
      const t = el.innerText?.trim()
      if (t && t.length > 15 && t.length < 1000 && !caption) {
        caption = t
      }
    })

    // Image
    let imageUrl = ''
    const img = article.querySelector('img[srcset], img[src]')
    if (img) {
      imageUrl = img.srcset?.split(',')[0]?.split(' ')[0] || img.src
    }

    // Username
    let username = ''
    const userEl = article.querySelector('a[href*="/"] span, header a span')
    if (userEl) username = userEl.innerText?.trim()

    if (caption || imageUrl) {
      posts.push({
        index,
        caption: caption.slice(0, 300),
        imageUrl,
        username: username || 'Unknown',
        preview: caption.slice(0, 80) || 'Image post',
      })
    }
  })

  // Fallback — generic page scrape if no articles found
  if (posts.length === 0) {
    const captions = []
    document.querySelectorAll('p, span, div, h1, h2, li').forEach(el => {
      if (el.children.length === 0) {
        const t = el.innerText?.trim()
        if (t && t.length > 20 && t.length < 600) captions.push(t)
      }
    })

    const imageUrls = []
    document.querySelectorAll('img').forEach(img => {
      if (img.src?.startsWith('http') && img.width > 80) imageUrls.push(img.src)
    })

    if (captions.length > 0) {
      posts.push({
        index: 0,
        caption: [...new Set(captions)].slice(0, 5).join(' ').slice(0, 500),
        imageUrl: imageUrls[0] || '',
        username: window.location.hostname,
        preview: captions[0].slice(0, 80),
      })
    }
  }

  return {
    platform: window.location.hostname.includes('instagram.com') ? 'instagram'
            : window.location.hostname.includes('whatsapp.com') ? 'whatsapp'
            : 'webpage',
    posts: posts.slice(0, 6),
    pageUrl: window.location.href,
    pageTitle: document.title,
  }
}

window._scamshieldExtract = extractInstagramPosts