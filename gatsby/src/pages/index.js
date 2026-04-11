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

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#0f0a1a",
    color: "#e2e0ea",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  header: {
    background: "linear-gradient(135deg, #1a0f2e 0%, #0d1117 50%, #0a1628 100%)",
    borderBottom: "3px solid #7c3aed",
    padding: "32px 24px",
    textAlign: "center",
  },
  title: {
    fontSize: "2.5rem",
    fontWeight: 800,
    margin: 0,
    background: "linear-gradient(90deg, #a78bfa, #34d399)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    fontSize: "1.1rem",
    color: "#9ca3af",
    marginTop: "8px",
    marginBottom: "16px",
  },
  langBar: {
    display: "flex",
    justifyContent: "center",
    gap: "12px",
    marginTop: "16px",
  },
  langBtn: {
    display: "inline-block",
    padding: "8px 24px",
    borderRadius: "8px",
    fontWeight: 700,
    fontSize: "0.95rem",
    textDecoration: "none",
    transition: "transform 0.15s, box-shadow 0.15s",
  },
  langBtnUA: {
    backgroundColor: "#7c3aed",
    color: "#fff",
    border: "2px solid #7c3aed",
  },
  langBtnEN: {
    backgroundColor: "transparent",
    color: "#34d399",
    border: "2px solid #34d399",
  },
  main: {
    maxWidth: "960px",
    margin: "0 auto",
    padding: "32px 16px",
  },
  sectionTitle: {
    fontSize: "1.3rem",
    fontWeight: 700,
    color: "#a78bfa",
    marginBottom: "20px",
    paddingBottom: "8px",
    borderBottom: "1px solid #2d2640",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "20px",
    marginBottom: "40px",
  },
  card: {
    backgroundColor: "#1a1230",
    borderRadius: "12px",
    border: "1px solid #2d2640",
    overflow: "hidden",
    transition: "transform 0.2s, border-color 0.2s",
  },
  cardImage: {
    width: "100%",
    height: "180px",
    objectFit: "cover",
    display: "block",
  },
  cardImagePlaceholder: {
    width: "100%",
    height: "180px",
    background: "linear-gradient(135deg, #1e1438, #0d1a2d)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "3rem",
  },
  cardBody: {
    padding: "16px",
  },
  cardMeta: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "8px",
    fontSize: "0.8rem",
  },
  badge: {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "0.75rem",
    fontWeight: 700,
    textTransform: "uppercase",
    color: "#fff",
  },
  cardDate: {
    color: "#6b7280",
    fontSize: "0.8rem",
  },
  cardTitle: {
    fontSize: "1.05rem",
    fontWeight: 700,
    color: "#e2e0ea",
    lineHeight: 1.3,
    margin: "0 0 8px 0",
  },
  cardDesc: {
    fontSize: "0.85rem",
    color: "#9ca3af",
    lineHeight: 1.5,
    margin: 0,
  },
  cardLink: {
    textDecoration: "none",
    color: "inherit",
    display: "block",
  },
  characterTag: {
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
  emptyState: {
    textAlign: "center",
    padding: "64px 16px",
    color: "#6b7280",
    fontSize: "1.1rem",
  },
}

const CHARACTER_EMOJI = {
  ender: "\uD83C\uDFAE",
  dad: "\uD83E\uDDD4",
}

function ArticleCard({ article }) {
  const type = article.frontmatter.type || "news"
  const character = article.frontmatter.character || "ender"
  const lang = article.frontmatter.lang || "en"
  const slug = article.frontmatter.slug

  return (
    <Link to={`/${lang}/${slug}/`} style={styles.cardLink}>
      <div
        style={styles.card}
        onMouseEnter={e => {
          e.currentTarget.style.transform = "translateY(-4px)"
          e.currentTarget.style.borderColor = "#7c3aed"
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = "translateY(0)"
          e.currentTarget.style.borderColor = "#2d2640"
        }}
      >
        {article.frontmatter.image ? (
          <img
            src={article.frontmatter.image}
            alt={article.frontmatter.title}
            style={styles.cardImage}
          />
        ) : (
          <div style={styles.cardImagePlaceholder}>
            {CHARACTER_EMOJI[character] || "\uD83C\uDFAE"}
          </div>
        )}
        <div style={styles.cardBody}>
          <div style={styles.cardMeta}>
            <span
              style={{
                ...styles.badge,
                backgroundColor: TYPE_COLORS[type] || "#7c3aed",
              }}
            >
              {TYPE_LABELS[type] || type}
            </span>
            <span style={styles.cardDate}>{article.frontmatter.date}</span>
            <span style={styles.characterTag}>
              {CHARACTER_EMOJI[character]}
            </span>
          </div>
          <h3 style={styles.cardTitle}>{article.frontmatter.title}</h3>
          {article.frontmatter.description && (
            <p style={styles.cardDesc}>{article.frontmatter.description}</p>
          )}
        </div>
      </div>
    </Link>
  )
}

export default function IndexPage({ data }) {
  const articles = data.allMarkdownRemark.nodes
  const enArticles = articles.filter(a => a.frontmatter.lang === "en")
  const uaArticles = articles.filter(a => a.frontmatter.lang === "ua")

  const recentEN = enArticles.slice(0, 6)
  const recentUA = uaArticles.slice(0, 6)

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}>Ender</h1>
        <p style={styles.subtitle}>
          Roblox news, guides, lifehacks, game reviews
        </p>
        <div style={styles.langBar}>
          <Link to="/ua/" style={{ ...styles.langBtn, ...styles.langBtnUA }}>
            UA
          </Link>
          <Link to="/en/" style={{ ...styles.langBtn, ...styles.langBtnEN }}>
            EN
          </Link>
        </div>
      </header>

      <main style={styles.main}>
        {articles.length === 0 ? (
          <div style={styles.emptyState}>
            <p>No articles yet. Check back soon!</p>
          </div>
        ) : (
          <>
            {recentEN.length > 0 && (
              <>
                <h2 style={styles.sectionTitle}>Latest in English</h2>
                <div style={styles.grid}>
                  {recentEN.map(article => (
                    <ArticleCard
                      key={article.id}
                      article={article}
                    />
                  ))}
                </div>
              </>
            )}

            {recentUA.length > 0 && (
              <>
                <h2 style={styles.sectionTitle}>Latest in Ukrainian</h2>
                <div style={styles.grid}>
                  {recentUA.map(article => (
                    <ArticleCard
                      key={article.id}
                      article={article}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </main>

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

export function Head() {
  return (
    <>
      <title>Ender — Roblox Media</title>
      <meta
        name="description"
        content="Roblox news, guides, lifehacks, game reviews by EnderFaion"
      />
      <meta name="theme-color" content="#0f0a1a" />
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
    </>
  )
}

export const query = graphql`
  query IndexPage {
    allMarkdownRemark(
      sort: { frontmatter: { date: DESC } }
      limit: 20
    ) {
      nodes {
        id
        frontmatter {
          title
          slug
          date(formatString: "YYYY-MM-DD")
          type
          lang
          image
          description
          character
        }
      }
    }
  }
`
