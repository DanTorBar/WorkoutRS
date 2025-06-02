/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack(config) {
    // Primero excluimos los svg de las reglas por defecto:
    const fileLoaderRule = config.module.rules.find(rule =>
      rule.test?.test?.('.svg')
    )
    fileLoaderRule.exclude = /\.svg$/

    // Ahora añadimos SVGR para svg:
    config.module.rules.push({
      test: /\.svg$/,
      issuer: /\.[jt]sx?$/,
      use: [
        {
          loader: '@svgr/webpack',
          options: {
            icon: true,
            // puedes añadir svgr options aquí
          },
        },
      ],
    })

    return config
  },
}

module.exports = nextConfig
