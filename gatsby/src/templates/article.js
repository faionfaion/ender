import React from "react"
import { graphql, Link } from "gatsby"

const TYPE_COLORS = {
  news: "#7c3aed",
  guide: "#059669",
  review: "#d97706",
  lifehack: "#2563eb",
  top: "#dc2626",
}

const TYPE_LABELS = {
  news: "News",
  guide: "Guide",
  review: "Review",
  lifehack: "Lifehack",
  top: "Top List",
}

const CHARACTER_EMOJI = {
  ender: "\uD83C\uDFAE",
  dad: "\uD83E\uDDD4",
}

const CHARACTER_NAMES = {
  ender: "EnderFaion",
  dad: "FaionEnder",
}

const TG_CHANNELS = {
  ua: "ender_faion_ua",
  en: "ender_faion_en",
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#0f0a1a",
    color: "#e2e0ea",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  nav: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 24px",
    borderBottom: "1px solid #2d2640",
    backgroundColor: "#1a0f2e",
  },
  navBrand: {
    fontSize: "1.3rem",
    fontWeight: 800,
    textDecoration: "none",
    background: "linear-gradient(90deg, #a78bfa, #34d399)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  navLinks: {
    display: "flex",
    gap: "16px",
  },
  navLink: {
    color: "#9ca3af",
    textDecoration: "none",
    fontSize: "0.9rem",
    fontWeight: 600,
  },
  article: {
    maxWidth: "720px",
    margin: "0 auto",
    padding: "40px 16px",
  },
  heroImage: {
    width: "100%",
    maxHeight: "500px",
    objectFit: "cover",
    borderRadius: "12px",
    marginBottom: "24px",
  },
  meta: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    gap: "12px",
    marginBottom: "16px",
    fontSize: "0.85rem",
    color: "#9ca3af",
  },
  badge: {
    display: "inline-block",
    padding: "3px 10px",
    borderRadius: "4px",
    fontSize: "0.75rem",
    fontWeight: 700,
    textTransform: "uppercase",
    color: "#fff",
  },
  title: {
    fontSize: "2rem",
    fontWeight: 800,
    lineHeight: 1.2,
    margin: "0 0 16px 0",
    color: "#f3f0ff",
  },
  description: {
    fontSize: "1.1rem",
    color: "#9ca3af",
    lineHeight: 1.6,
    marginBottom: "24px",
    fontStyle: "italic",
  },
  tags: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
    marginBottom: "24px",
  },
  tag: {
    display: "inline-block",
    padding: "4px 12px",
    borderRadius: "16px",
    backgroundColor: "#2d2640",
    color: "#a78bfa",
    fontSize: "0.8rem",
    fontWeight: 600,
    textDecoration: "none",
    transition: "background-color 0.15s",
  },
  body: {
    fontSize: "1.05rem",
    lineHeight: 1.75,
    color: "#d1cfe0",
  },
  tgLink: {
    display: "inline-block",
    marginTop: "32px",
    padding: "12px 24px",
    borderRadius: "8px",
    backgroundColor: "#7c3aed",
    color: "#fff",
    textDecoration: "none",
    fontWeight: 700,
    fontSize: "0.95rem",
    transition: "background-color 0.15s",
  },
  prevNext: {
    display: "flex",
    justifyContent: "space-between",
    marginTop: "48px",
    paddingTop: "24px",
    borderTop: "1px solid #2d2640",
  },
  prevNextLink: {
    color: "#a78bfa",
    textDecoration: "none",
    fontSize: "0.9rem",
    fontWeight: 600,
  },
  alternateLink: {
    display: "inline-block",
    marginTop: "16px",
    padding: "8px 16px",
    borderRadius: "6px",
    border: "1px solid #2d2640",
    color: "#9ca3af",
    textDecoration: "none",
    fontSize: "0.85rem",
  },
  relatedSection: {
    marginTop: "48px",
    paddingTop: "24px",
    borderTop: "1px solid #2d2640",
  },
  relatedTitle: {
    fontSize: "1.2rem",
    fontWeight: 700,
    color: "#a78bfa",
    marginBottom: "16px",
  },
  relatedGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
    gap: "16px",
  },
  relatedCard: {
    backgroundColor: "#1a1230",
    borderRadius: "8px",
    border: "1px solid #2d2640",
    padding: "16px",
    textDecoration: "none",
    color: "inherit",
    display: "block",
    transition: "border-color 0.15s",
  },
  relatedCardTitle: {
    fontSize: "0.9rem",
    fontWeight: 700,
    color: "#e2e0ea",
    margin: "0 0 4px 0",
    lineHeight: 1.3,
  },
  relatedCardMeta: {
    fontSize: "0.75rem",
    color: "#6b7280",
  },
  footer: {
    textAlign: "center",
    padding: "32px 16px",
    borderTop: "1px solid #2d2640",
    color: "#6b7280",
    fontSize: "0.85rem",
  },
}

export default function ArticleTemplate({ data, pageContext }) {
  const { markdownRemark: post } = data
  const { frontmatter, html } = post
  const {
    readingTime,
    alternateUrl,
    alternateLang,
    relatedArticles: relatedJSON,
    prevArticle: prevJSON,
    nextArticle: nextJSON,
  } = pageContext

  const type = frontmatter.type || "news"
  const character = frontmatter.character || "ender"
  const lang = frontmatter.lang || "en"
  const tags = frontmatter.tags || []
  const tgChannel = TG_CHANNELS[lang]

  const related = relatedJSON ? JSON.parse(relatedJSON) : []
  const prevArticle = prevJSON ? JSON.parse(prevJSON) : null
  const nextArticle = nextJSON ? JSON.parse(nextJSON) : null

  const langLabels = {
    en: "Read in Ukrainian",
    ua: "Read in English",
  }

  return (
    <div style={styles.page}>
      <nav style={styles.nav}>
        <Link to="/" style={styles.navBrand}>Ender</Link>
        <div style={styles.navLinks}>
          <Link to="/ua/" style={styles.navLink}>UA</Link>
          <Link to="/en/" style={styles.navLink}>EN</Link>
        </div>
      </nav>

      <article style={styles.article}>
        {frontmatter.image && (
          <img
            src={frontmatter.image}
            alt={frontmatter.title}
            style={styles.heroImage}
          />
        )}

        <div style={styles.meta}>
          <span
            style={{
              ...styles.badge,
              backgroundColor: TYPE_COLORS[type] || "#7c3aed",
            }}
          >
            {TYPE_LABELS[type] || type}
          </span>
          <span>{frontmatter.date}</span>
          <span>{CHARACTER_EMOJI[character]} {CHARACTER_NAMES[character]}</span>
          {readingTime > 0 && <span>{readingTime} min read</span>}
        </div>

        <h1 style={styles.title}>{frontmatter.title}</h1>

        {frontmatter.description && (
          <p style={styles.description}>{frontmatter.description}</p>
        )}

        {tags.length > 0 && (
          <div style={styles.tags}>
            {tags.map(tag => (
              <Link
                key={tag}
                to={`/${lang}/tag/${tag}/`}
                style={styles.tag}
              >
                #{tag}
              </Link>
            ))}
          </div>
        )}

        <div
          style={styles.body}
          dangerouslySetInnerHTML={{ __html: html }}
        />

        {tgChannel && (
          <a
            href={`https://t.me/${tgChannel}`}
            target="_blank"
            rel="noopener noreferrer"
            style={styles.tgLink}
          >
            {lang === "ua" ? "Telegram канал" : "Follow on Telegram"}
          </a>
        )}

        {alternateUrl && (
          <div>
            <Link to={alternateUrl} style={styles.alternateLink}>
              {langLabels[lang] || "Read in another language"}
            </Link>
          </div>
        )}

        {related.length > 0 && (
          <div style={styles.relatedSection}>
            <h2 style={styles.relatedTitle}>
              {lang === "ua" ? "Схожі статті" : "Related Articles"}
            </h2>
            <div style={styles.relatedGrid}>
              {related.map(r => (
                <Link
                  key={r.slug}
                  to={`/${r.lang}/${r.slug}/`}
                  style={styles.relatedCard}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = "#7c3aed" }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = "#2d2640" }}
                >
                  <h3 style={styles.relatedCardTitle}>{r.title}</h3>
                  <div style={styles.relatedCardMeta}>
                    {r.date} &middot; {r.type || "news"}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        <div style={styles.prevNext}>
          <div>
            {prevArticle && (
              <Link
                to={`/${prevArticle.lang}/${prevArticle.slug}/`}
                style={styles.prevNextLink}
              >
                &larr; {prevArticle.title}
              </Link>
            )}
          </div>
          <div>
            {nextArticle && (
              <Link
                to={`/${nextArticle.lang}/${nextArticle.slug}/`}
                style={styles.prevNextLink}
              >
                {nextArticle.title} &rarr;
              </Link>
            )}
          </div>
        </div>
      </article>

      <footer style={styles.footer}>
        <p>Ender — Roblox Media by EnderFaion</p>
        <p>
          <a
            href="https://t.me/ender_faion_ua"
            style={{ color: "#7c3aed", textDecoration: "none", marginRight: "16px" }}
          >
            Telegram UA
          </a>
          <a
            href="https://t.me/ender_faion_en"
            style={{ color: "#34d399", textDecoration: "none" }}
          >
            Telegram EN
          </a>
        </p>
      </footer>
    </div>
  )
}

export function Head({ data }) {
  const { frontmatter } = data.markdownRemark
  return (
    <>
      <title>{frontmatter.title} | Ender</title>
      <meta name="description" content={frontmatter.description || ""} />
      <meta name="theme-color" content="#0f0a1a" />
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
    </>
  )
}

export const query = graphql`
  query ArticlePage($id: String!) {
    markdownRemark(id: { eq: $id }) {
      html
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
    }
  }
`
