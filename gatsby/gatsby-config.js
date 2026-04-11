/**
 * Gatsby configuration for Ender — Roblox Media
 * https://ender.faion.net
 */

/** @type {import('gatsby').GatsbyConfig} */
module.exports = {
  siteMetadata: {
    title: "Ender — Roblox Media",
    description: "Roblox news, guides, lifehacks, game reviews by EnderFaion",
    siteUrl: "https://ender.faion.net",
  },
  plugins: [
    {
      resolve: "gatsby-source-filesystem",
      options: {
        name: "content",
        path: `${__dirname}/../content`,
      },
    },
    {
      resolve: "gatsby-source-filesystem",
      options: {
        name: "images",
        path: `${__dirname}/static/images`,
      },
    },
    "gatsby-transformer-remark",
    "gatsby-plugin-sharp",
    "gatsby-transformer-sharp",
    "gatsby-plugin-image",
    {
      resolve: "gatsby-plugin-sitemap",
      options: {
        query: `
          {
            site {
              siteMetadata {
                siteUrl
              }
            }
            allSitePage {
              nodes {
                path
              }
            }
          }
        `,
        resolveSiteUrl: ({ site }) => site.siteMetadata.siteUrl,
        serialize: ({ path }) => ({
          url: path,
          changefreq: "daily",
          priority: path === "/" ? 1.0 : path.match(/^\/(en|ua)\/$/) ? 0.9 : 0.7,
        }),
      },
    },
  ],
};
