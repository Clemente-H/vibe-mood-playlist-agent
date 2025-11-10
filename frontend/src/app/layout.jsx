import { Geist, Geist_Mono, Permanent_Marker } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const titlefont = Permanent_Marker({
  variable: "--font-handwriting",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata = {
  title: "Vibe.FM",
  description: "A music agent that understands your emotions",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${titlefont.variable} antialiased`}
      >
        {children}
        <Toaster position="top-center"/>
      </body>

    </html>
  );
}
