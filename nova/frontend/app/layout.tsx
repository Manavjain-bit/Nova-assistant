import "./globals.css";

export const metadata = {
  title: "Nova - AI Voice Personal Assistant",
  description: "Your premium AI voice personal assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="font-body bg-bg text-text min-h-screen">{children}</body>
    </html>
  );
}
