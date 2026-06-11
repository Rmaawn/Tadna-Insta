import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/components/LanguageProvider";

export const metadata: Metadata = {
  title: "Tadna Insta — AI Instagram Growth Intelligence",
  description:
    "An AI Instagram growth strategist. Analyze any public profile and get premium, data-driven growth recommendations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Default to Persian / RTL; LanguageProvider updates this live on the client.
  return (
    <html lang="fa" dir="rtl">
      <body className="min-h-screen font-sans">
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
