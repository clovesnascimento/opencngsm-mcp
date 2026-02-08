import { useState } from 'react'

export default function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">🤖</div>
            <div>
              <h1 className="text-2xl font-bold">OpenCngsm MCP</h1>
              <p className="text-sm text-blue-100">Multi-Model Cognitive Platform v2.0</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm">Online</span>
          </div>
        </div>
      </div>
    </header>
  )
}
