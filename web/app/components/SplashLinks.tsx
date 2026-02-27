export default function SplashLinks() {
  const sizes = [
    "640x1136",
    "750x1334",
    "828x1792",
    "1125x2436",
    "1242x2208",
    "1242x2688",
    "1536x2048",
    "1668x2224",
    "1668x2388",
    "2048x2732",
  ];

  return (
    <>
      {sizes.map((size) => (
        <link
          key={size}
          rel="apple-touch-startup-image"
          href={`/splash/splash-${size}.png`}
        />
      ))}
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      <meta name="apple-mobile-web-app-title" content="Ledgerlane" />
    </>
  );
}
