import React from "react"
import { Link } from "gatsby"

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

const LANG_LABELS = {
  en: { title: "English", switchTo: "UA", switchLang: "ua" },
  ua: { title: "Ukrainian", switchTo: "EN", switchLang: "en" },
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
  navLink: {
    color: "#9ca3af",
    textDecoration: "none",
    fontSize: "0.9rem",
    fontWeight: 600,
    padding: "6px 16px",
    borderRadius: "6px",
    border: "1px solid #2d2640",
  },
  main: {
    maxWidth: "960px",
    margin: "0 auto",
    padding: "32px 16px",
  },
  pageTitle: {
    fontSize: "1.5rem",
    fontWeight: 700,
    color: "#a78bfa",
    marginBottom: "8px",
  },
  stats: {
    fontSize: "0.85rem",
    color: "#6b7280",
    marginBottom: "32px",
  },
  dateGroup: {
    marginBottom: "32px",
  },
  dateHeading: {
    fontSize: "1rem",
    fontWeight: 700,
    color: "#34d399",
    marginBottom: "12px",
    paddingBottom: "6px",
    borderBottom: "1px solid #2d2640",
  },
  articleList: {
    listStyle: "none",
    padding: 0,
    margin: 0,
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  articleItem: {
    backgroundColor: "#1a1230",
    borderRadius: "8px",
    border: "1px solid #2d2640",
    padding: "16px",
    textDecoration: "none",
    color: "inherit",
    display: "flex",
    gap: "12px",
    alignItems: "flex-start",
    transition: "border-color 0.15s",
  },
  articleMeta: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "4px",
    fontSize: "0.8rem",
  },
  badge: {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "0.7rem",
    fontWeight: 700,
    textTransform: "uppercase",
    color: "#fff",
  },
  articleTitle: {
    fontSize: "1rem",
    fontWeight: 700,
    color: "#e2e0ea",
    margin: 0,
    lineHeight: 1.3,
  },
  articleDesc: {
    fontSize: "0.8rem",
    color: "#9ca3af",
    marginTop: "4px",
    lineHeight: 1.4,
  },
  footer: {
    textAlign: "center",
    padding: "32px 16px",
    borderTop: "1px solid #2d2640",
    color: "#6b7280",
    fontSize: "0.85rem",
  },
}

export default function LangIndexTemplate({ pageContext }) {
  const { lang, langName, byDate: byDateJSON, sortedDates: datesJSON, articleCount } = pageContext
  const byDate = JSON.parse(byDateJSON)
  const sortedDates = JSON.parse(datesJSON)
  const langInfo = LANG_LABELS[lang] || LANG_LABELS.en

  return (
    <div style={styles.page}>
      <nav style={styles.nav}>
        <Link to="/" style={styles.navBrand}>Ender</Link>
        <Link to={`/${langInfo.switchLang}/`} style={styles.navLink}>
          {langInfo.switchTo}
        </Link>
      </nav>

      <main style={styles.main}>
        <h1 style={styles.pageTitle}>
          {lang === "ua" ? "Всі статті" : "All Articles"} ({langName})
        </h1>
        <p style={styles.stats}>
          {articleCount} {lang === "ua" ? "статей" : "articles"}
        </p>

        {sortedDates.map(date => (
          <div key={date} style={styles.dateGroup}>
            <h2 style={styles.dateHeading}>{date}</h2>
            <div style={styles.articleList}>
              {byDate[date].map(article => {
                const type = article.type || "news"
                const character = article.character || "ender"
                return (
                  <Link
                    key={article.slug}
                    to={`/${article.lang}/${article.slug}/`}
                    style={styles.articleItem}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = "#7c3aed" }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = "#2d2640" }}
                  >
                    <div>
                      <div style={styles.articleMeta}>
                        <span
                          style={{
                            ...styles.badge,
                            backgroundColor: TYPE_COLORS[type] || "#7c3aed",
                          }}
                        >
                          {TYPE_LABELS[type] || type}
                        </span>
                        <span style={{ color: "#6b7280" }}>
                          {CHARACTER_EMOJI[character]}
                        </span>
                        {article.readingTime > 0 && (
                          <span style={{ color: "#6b7280" }}>
                            {article.readingTime} min
                          </span>
                        )}
                      </div>
                      <h3 style={styles.articleTitle}>{article.title}</h3>
                      {article.description && (
                        <p style={styles.articleDesc}>{article.description}</p>
                      )}
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </main>

      <footer style={styles.footer}>
        <p>Ender — Roblox Media by EnderFaion</p>
      </footer>
    </div>
  )
}

export function Head({ pageContext }) {
  const { lang, langName } = pageContext
  const titlePrefix = lang === "ua" ? "Всі статті" : "All Articles"
  return (
    <>
      <title>{titlePrefix} | Ender</title>
      <meta
        name="description"
        content={`Roblox articles in ${langName} by EnderFaion`}
      />
      <meta name="theme-color" content="#0f0a1a" />
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
    </>
  )
}
