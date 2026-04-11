/**
 * Gatsby Node APIs for Ender — Roblox Media
 *
 * Creates:
 * - Article pages: /{lang}/{slug}/
 * - Language index pages: /en/, /ua/
 * - Tag pages: /{lang}/tag/{tagname}/
 */

const path = require("path")

/** @type {import('gatsby').GatsbyNode['createSchemaCustomization']} */
exports.createSchemaCustomization = ({ actions }) => {
  const { createTypes } = actions
  createTypes(`
    type MarkdownRemarkFrontmatter {
      title: String
      slug: String
      date: Date @dateformat
      type: String
      lang: String
      tags: [String]
      image: String
      description: String
      author: String
      character: String
      tg_post: String
    }
    type MarkdownRemark implements Node {
      frontmatter: MarkdownRemarkFrontmatter
    }
  `)
}

/** @type {import('gatsby').GatsbyNode['createPages']} */
exports.createPages = async ({ graphql, actions, reporter }) => {
  const { createPage } = actions

  const result = await graphql(`
    {
      allMarkdownRemark(sort: { frontmatter: { date: DESC } }) {
        nodes {
          frontmatter {
            title
            slug
            date(formatString: "YYYY-MM-DD")
            type
            lang
            tags
            image
            description
            author
            character
            tg_post
          }
          html
          id
        }
      }
    }
  `)

  if (result.errors) {
    reporter.panicOnBuild("Error loading markdown content", result.errors)
    return
  }

  const articles = result.data.allMarkdownRemark.nodes

  // --- Reading time ---
  const readingTimeMap = new Map()
  articles.forEach(article => {
    const text = (article.html || "").replace(/<[^>]*>/g, "")
    const wordCount = text.trim().split(/\s+/).filter(Boolean).length
    readingTimeMap.set(article.id, Math.ceil(wordCount / 200))
  })

  // --- Hreflang pairs (EN <-> UA) ---
  const pairMap = new Map()
  const enSlugs = new Map()
  const uaSlugs = new Map()

  articles.forEach(article => {
    const { lang, slug } = article.frontmatter
    if (!lang || !slug) return
    if (lang === "en") enSlugs.set(slug, article)
    if (lang === "ua") uaSlugs.set(slug, article)
  })

  uaSlugs.forEach((uaArticle, uaSlug) => {
    if (!uaSlug.endsWith("-ua")) return
    const enSlug = uaSlug.slice(0, -3)
    if (!enSlugs.has(enSlug)) return

    pairMap.set(`ua:${uaSlug}`, {
      alternateUrl: `/en/${enSlug}/`,
      alternateLang: "en",
    })
    pairMap.set(`en:${enSlug}`, {
      alternateUrl: `/ua/${uaSlug}/`,
      alternateLang: "uk",
    })
  })

  reporter.info(
    `[hreflang] Paired ${pairMap.size / 2} EN/UA article pairs. ` +
    `Total: ${articles.length} articles.`
  )

  // --- Related articles (by tag overlap) ---
  const relatedMap = new Map()
  articles.forEach(articleA => {
    const { lang: langA, slug: slugA, tags: tagsA } = articleA.frontmatter
    if (!langA || !slugA) return

    const setA = new Set(tagsA || [])
    const scored = []

    articles.forEach((articleB, indexB) => {
      const { lang: langB, slug: slugB, tags: tagsB } = articleB.frontmatter
      if (!langB || !slugB) return
      if (langB !== langA || slugB === slugA) return

      let score = 0
      ;(tagsB || []).forEach(t => { if (setA.has(t)) score++ })
      scored.push({ article: articleB, score, index: indexB })
    })

    scored.sort((a, b) => b.score - a.score || a.index - b.index)

    const withOverlap = scored.filter(s => s.score >= 1).slice(0, 4)
    let related = [...withOverlap]

    if (related.length < 3) {
      const usedSlugs = new Set(related.map(r => r.article.frontmatter.slug))
      usedSlugs.add(slugA)
      for (const s of scored) {
        if (related.length >= 3) break
        if (!usedSlugs.has(s.article.frontmatter.slug)) {
          related.push(s)
          usedSlugs.add(s.article.frontmatter.slug)
        }
      }
    }

    relatedMap.set(articleA.id, related.map(r => ({
      slug: r.article.frontmatter.slug,
      title: r.article.frontmatter.title,
      date: r.article.frontmatter.date,
      type: r.article.frontmatter.type,
      lang: r.article.frontmatter.lang,
      image: r.article.frontmatter.image,
      description: r.article.frontmatter.description,
      author: r.article.frontmatter.author || "EnderFaion",
      readingTime: readingTimeMap.get(r.article.id),
    })))
  })

  // --- Prev/next navigation (per language) ---
  const byLang = {}
  articles.forEach(article => {
    const { lang, slug } = article.frontmatter
    if (!lang || !slug) return
    if (!byLang[lang]) byLang[lang] = []
    byLang[lang].push(article)
  })

  const prevNextMap = new Map()
  Object.values(byLang).forEach(langArticles => {
    langArticles.forEach((article, i) => {
      const prev = i + 1 < langArticles.length ? langArticles[i + 1] : null
      const next = i - 1 >= 0 ? langArticles[i - 1] : null
      prevNextMap.set(article.id, {
        prevArticle: prev ? { slug: prev.frontmatter.slug, title: prev.frontmatter.title, lang: prev.frontmatter.lang } : null,
        nextArticle: next ? { slug: next.frontmatter.slug, title: next.frontmatter.title, lang: next.frontmatter.lang } : null,
      })
    })
  })

  // --- Article pages ---
  const articleTemplate = path.resolve("src/templates/article.js")
  articles.forEach(article => {
    const { lang, slug } = article.frontmatter
    if (!lang || !slug) return

    const pair = pairMap.get(`${lang}:${slug}`)
    const prevNext = prevNextMap.get(article.id) || { prevArticle: null, nextArticle: null }

    createPage({
      path: `/${lang}/${slug}/`,
      component: articleTemplate,
      context: {
        id: article.id,
        slug,
        lang,
        readingTime: readingTimeMap.get(article.id),
        alternateUrl: pair ? pair.alternateUrl : null,
        alternateLang: pair ? pair.alternateLang : null,
        relatedArticles: JSON.stringify(relatedMap.get(article.id) || []),
        prevArticle: prevNext.prevArticle ? JSON.stringify(prevNext.prevArticle) : null,
        nextArticle: prevNext.nextArticle ? JSON.stringify(prevNext.nextArticle) : null,
      },
    })
  })

  reporter.info(`Created ${articles.length} article pages`)

  // --- Language index pages ---
  const langIndexTemplate = path.resolve("src/templates/lang-index.js")
  const languages = { en: "English", ua: "Ukrainian" }

  Object.entries(languages).forEach(([lang, langName]) => {
    const langArticles = articles.filter(a => a.frontmatter.lang === lang)

    const byDate = {}
    langArticles.forEach(a => {
      const date = a.frontmatter.date
      if (!date) return
      if (!byDate[date]) byDate[date] = []
      byDate[date].push({
        slug: a.frontmatter.slug,
        title: a.frontmatter.title,
        date: a.frontmatter.date,
        type: a.frontmatter.type,
        lang: a.frontmatter.lang,
        image: a.frontmatter.image,
        description: a.frontmatter.description,
        author: a.frontmatter.author || "EnderFaion",
        character: a.frontmatter.character || "ender",
        readingTime: readingTimeMap.get(a.id),
      })
    })

    const sortedDates = Object.keys(byDate).sort().reverse()
    const recentDates = sortedDates.slice(0, 14)
    const recentByDate = {}
    recentDates.forEach(d => { recentByDate[d] = byDate[d] })

    createPage({
      path: `/${lang}/`,
      component: langIndexTemplate,
      context: {
        lang,
        langName,
        byDate: JSON.stringify(recentByDate),
        sortedDates: JSON.stringify(recentDates),
        articleCount: langArticles.length,
        totalDays: sortedDates.length,
      },
    })
  })

  reporter.info("Created language index pages: /en/, /ua/")

  // --- Tag pages (language-scoped) ---
  const tagTemplate = path.resolve("src/templates/tag.js")
  const tagMap = {}

  articles.forEach(article => {
    const { lang, tags: articleTags } = article.frontmatter
    if (!lang) return
    ;(articleTags || []).forEach(tag => {
      if (!tagMap[lang]) tagMap[lang] = {}
      if (!tagMap[lang][tag]) tagMap[lang][tag] = []
      tagMap[lang][tag].push({
        slug: article.frontmatter.slug,
        title: article.frontmatter.title,
        date: article.frontmatter.date,
        type: article.frontmatter.type,
        lang: article.frontmatter.lang,
        image: article.frontmatter.image,
        description: article.frontmatter.description,
        author: article.frontmatter.author || "EnderFaion",
        readingTime: readingTimeMap.get(article.id),
      })
    })
  })

  let tagPageCount = 0
  Object.entries(tagMap).forEach(([lang, langTags]) => {
    Object.entries(langTags).forEach(([tag, tagArticles]) => {
      const otherLang = lang === "en" ? "ua" : "en"
      const hasAlternate = tagMap[otherLang] && tagMap[otherLang][tag]

      createPage({
        path: `/${lang}/tag/${tag}/`,
        component: tagTemplate,
        context: {
          tag,
          lang,
          articles: JSON.stringify(tagArticles),
          articleCount: tagArticles.length,
          alternateUrl: hasAlternate ? `/${otherLang}/tag/${tag}/` : null,
        },
      })
      tagPageCount++
    })
  })

  reporter.info(`Created ${tagPageCount} tag pages (language-scoped)`)
}
