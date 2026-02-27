import "./globals.css";

import PwaRegister from "./components/PwaRegister";
import SplashLinks from "./components/SplashLinks";

export const metadata = {
  title: "Bookkeeping",
  description: "Multi-business bookkeeping workspace",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/icons/icon-192.png",
    apple: "/icons/icon-180.png",
  },
  themeColor: "#f97316",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <SplashLinks />
      </head>
      <body>
        <PwaRegister />
        {children}
      </body>
    </html>
  );
}
