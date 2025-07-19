
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AgentProvider, useAgent } from '@/stores/agentStore'
import { useChatStore } from '@/stores/chatStore'
import { Layout } from '@/components/Layout'
import { AgentSelector } from '@/components/agents/AgentSelector'
import { ChatInterface } from '@/components/ChatInterface'
import { useState } from 'react'
import { ChevronLeft, ChevronRight, MessageSquare, Users, Activity, Settings, History, Plus } from 'lucide-react'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

// Main app content component that can use hooks
function AppContent() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { activeAgent } = useAgent()
  const { createSession } = useChatStore()

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  const handleNewChatSession = () => {
    if (activeAgent) {
      const newSession = createSession(activeAgent.id)
      console.log('Created new chat session:', newSession)
      // Close mobile menu if open
      setMobileMenuOpen(false)
    } else {
      console.warn('No active agent selected for new chat session')
    }
  }

  return (
    <div className="flex flex-col h-full">
            {/* Header with Agent Selection */}
            <header className="border-b border-gray-200 bg-white">
              <div className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {/* Mobile Menu Button */}
                    <button
                      onClick={toggleMobileMenu}
                      className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
                      title="Toggle menu"
                    >
                      <MessageSquare className="w-5 h-5 text-gray-600" />
                    </button>

                    <h1 className="text-2xl font-bold text-gray-900">
                      MAGPIE
                    </h1>
                    <span className="hidden sm:block text-sm text-gray-500">
                      Multi-Agent Platform for Intelligent Execution
                    </span>
                  </div>
                  <AgentSelector />
                </div>
              </div>
            </header>

            {/* Main Content Area */}
            <main className="flex-1 flex overflow-hidden relative">
              {/* Mobile Overlay */}
              {mobileMenuOpen && (
                <div
                  className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
                  onClick={() => setMobileMenuOpen(false)}
                />
              )}

              {/* Collapsible Sidebar */}
              <aside className={`${
                sidebarCollapsed ? 'w-16' : 'w-80'
              } ${
                mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
              } lg:relative fixed left-0 top-0 h-full z-50 border-r border-gray-200 bg-gray-50 transition-all duration-300 ease-in-out flex flex-col`}>

                {/* Sidebar Toggle Button */}
                <div className="p-4 border-b border-gray-200">
                  <button
                    onClick={toggleSidebar}
                    className="w-full flex items-center justify-center p-2 rounded-lg hover:bg-gray-200 transition-colors"
                    title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                  >
                    {sidebarCollapsed ? (
                      <ChevronRight className="w-5 h-5 text-gray-600" />
                    ) : (
                      <div className="flex items-center justify-between w-full">
                        <span className="text-sm font-medium text-gray-700">Navigation</span>
                        <ChevronLeft className="w-5 h-5 text-gray-600" />
                      </div>
                    )}
                  </button>
                </div>

                {/* Sidebar Content */}
                <div className="flex-1 overflow-y-auto p-4">
                  {!sidebarCollapsed ? (
                    <div className="space-y-6">
                      {/* Chat History Section */}
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                          <History className="w-4 h-4 mr-2" />
                          Chat History
                        </h3>
                        <div className="space-y-2">
                          <div className="p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 cursor-pointer transition-colors">
                            <div className="text-sm font-medium text-gray-900">Recent Session</div>
                            <div className="text-xs text-gray-500 mt-1">2 minutes ago</div>
                          </div>
                          <div className="p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 cursor-pointer transition-colors">
                            <div className="text-sm font-medium text-gray-900">Data Analysis</div>
                            <div className="text-xs text-gray-500 mt-1">1 hour ago</div>
                          </div>
                          <button className="w-full text-left text-sm text-primary-600 hover:text-primary-700 font-medium">
                            View all sessions →
                          </button>
                        </div>
                      </div>

                      {/* Agent Status Overview */}
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                          <Users className="w-4 h-4 mr-2" />
                          Agent Status
                        </h3>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between p-2 bg-white rounded border border-gray-200">
                            <span className="text-sm text-gray-900">Engineering Process</span>
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          </div>
                          <div className="flex items-center justify-between p-2 bg-white rounded border border-gray-200">
                            <span className="text-sm text-gray-900">Data Scientist</span>
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          </div>
                          <div className="flex items-center justify-between p-2 bg-white rounded border border-gray-200">
                            <span className="text-sm text-gray-900">General Chat</span>
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          </div>
                          <button className="w-full text-left text-sm text-primary-600 hover:text-primary-700 font-medium">
                            View all agents →
                          </button>
                        </div>
                      </div>

                      {/* System Status */}
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                          <Activity className="w-4 h-4 mr-2" />
                          System Status
                        </h3>
                        <div className="space-y-2">
                          <div className="p-3 bg-white rounded-lg border border-gray-200">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-900">Backend Connection</span>
                              <div className="flex items-center">
                                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                                <span className="text-xs text-green-600">Online</span>
                              </div>
                            </div>
                          </div>
                          <div className="p-3 bg-white rounded-lg border border-gray-200">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-900">Active Sessions</span>
                              <span className="text-sm font-medium text-gray-900">1</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Quick Actions */}
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                          <Settings className="w-4 h-4 mr-2" />
                          Quick Actions
                        </h3>
                        <div className="space-y-2">
                          <button
                            onClick={handleNewChatSession}
                            className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors group"
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="text-sm font-medium text-gray-900 flex items-center">
                                  <Plus className="w-4 h-4 mr-2 text-primary-600" />
                                  New Chat Session
                                </div>
                                <div className="text-xs text-gray-500 mt-1">
                                  Start fresh conversation with {activeAgent?.name || 'current agent'}
                                </div>
                              </div>
                            </div>
                          </button>
                          <button className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors">
                            <div className="text-sm font-medium text-gray-900">Agent Capabilities</div>
                            <div className="text-xs text-gray-500 mt-1">View agent specialties</div>
                          </button>
                          <button className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors">
                            <div className="text-sm font-medium text-gray-900">System Settings</div>
                            <div className="text-xs text-gray-500 mt-1">Configure preferences</div>
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* Collapsed Sidebar Icons */
                    <div className="space-y-4">
                      <button
                        onClick={handleNewChatSession}
                        className="w-full p-3 rounded-lg hover:bg-gray-200 transition-colors"
                        title="New Chat Session"
                      >
                        <Plus className="w-5 h-5 text-primary-600 mx-auto" />
                      </button>
                      <button
                        className="w-full p-3 rounded-lg hover:bg-gray-200 transition-colors"
                        title="Chat History"
                      >
                        <History className="w-5 h-5 text-gray-600 mx-auto" />
                      </button>
                      <button
                        className="w-full p-3 rounded-lg hover:bg-gray-200 transition-colors"
                        title="Agent Status"
                      >
                        <Users className="w-5 h-5 text-gray-600 mx-auto" />
                      </button>
                      <button
                        className="w-full p-3 rounded-lg hover:bg-gray-200 transition-colors"
                        title="System Status"
                      >
                        <Activity className="w-5 h-5 text-gray-600 mx-auto" />
                      </button>
                      <button
                        className="w-full p-3 rounded-lg hover:bg-gray-200 transition-colors"
                        title="Quick Actions"
                      >
                        <Settings className="w-5 h-5 text-gray-600 mx-auto" />
                      </button>
                    </div>
                  )}
                </div>
              </aside>

              {/* Chat Interface */}
              <div className="flex-1 flex flex-col">
                <ChatInterface />
              </div>
            </main>
          </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AgentProvider>
        <Layout>
          <AppContent />
        </Layout>
      </AgentProvider>
    </QueryClientProvider>
  )
}

export default App
