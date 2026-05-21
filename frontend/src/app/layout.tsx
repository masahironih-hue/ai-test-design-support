import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "業務系SE向け AIテスト設計支援ツール",
  description: "仕様メモからテスト観点・テストケース・確認事項を生成する支援ツールです。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
