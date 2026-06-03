import Chat from "@/app/components/Chat";

export default function Home() {
  return (
    <main className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-3 shrink-0">
        <span className="text-2xl">⚽</span>
        <div>
          <h1 className="text-lg font-bold text-gray-900 leading-tight">PL Stats AI</h1>
          <p className="text-xs text-gray-500">Premier League · Powered by Claude</p>
        </div>
      </header>

      {/* Chat fills remaining height */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full max-w-2xl mx-auto">
          <Chat />
        </div>
      </div>
    </main>
  );
}