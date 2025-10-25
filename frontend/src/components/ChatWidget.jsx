import React, { useState, useRef, useEffect } from 'react';
import { chatService } from '../services/chat';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your medical assistant. 👋",
      sender: 'bot',
      quickActions: [
        { label: '💊 What is Paracetamol?', query: 'what is paracetamol' },
        { label: '📊 Dosage Information', query: 'dosage information for paracetamol' },
        { label: '⚠️ Side Effects', query: 'side effects of paracetamol' },
        { label: '🔄 Drug Interactions', query: 'drug interactions of paracetamol' }
      ]
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatBotResponse = (text) => {
    // Format the response with better structure
    const lines = text.split('\n');
    return (
      <div className="space-y-2">
        {lines.map((line, index) => {
          // Check if line is a header (starts with **)
          if (line.includes('**')) {
            const cleanLine = line.replace(/\*\*/g, '');
            return (
              <div key={index} className="font-semibold text-indigo-700 text-sm">
                {cleanLine}
              </div>
            );
          }
          // Check if line is a bullet point
          else if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
            return (
              <div key={index} className="flex items-start text-sm">
                <span className="text-indigo-500 mr-2">•</span>
                <span className="text-gray-700">{line.replace(/^[•\-]\s*/, '')}</span>
              </div>
            );
          }
          // Regular text
          else if (line.trim()) {
            return (
              <div key={index} className="text-sm text-gray-700">
                {line}
              </div>
            );
          }
          return null;
        })}
      </div>
    );
  };

  const handleSend = async (query = null) => {
    const messageText = query || inputValue;
    if (!messageText.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: messageText,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Get bot response
      const response = await chatService.query(messageText);
      
      const botMessage = {
        id: messages.length + 2,
        text: response.answer,
        sender: 'bot',
        formatted: true
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        text: "Sorry, I'm having trouble understanding. Please try again.",
        sender: 'bot'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickAction = (query) => {
    handleSend(query);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {isOpen ? (
        <div className="w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col border border-gray-200 animate-fade-in">
          {/* Chat header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4 rounded-t-2xl flex justify-between items-center">
            <div className="flex items-center">
              <div className="h-10 w-10 bg-white rounded-full flex items-center justify-center mr-3">
                <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Medical Assistant</h3>
                <p className="text-xs text-indigo-100">Always here to help</p>
              </div>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-1 transition"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Chat messages */}
          <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-gray-50 to-white">
            {messages.map((message) => (
              <div key={message.id}>
                <div 
                  className={`mb-4 ${message.sender === 'user' ? 'text-right' : 'text-left'}`}
                >
                  <div 
                    className={`inline-block p-4 rounded-2xl max-w-[85%] ${
                      message.sender === 'user' 
                        ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-md' 
                        : 'bg-white border border-gray-200 shadow-sm'
                    }`}
                  >
                    {message.sender === 'bot' && message.formatted ? (
                      formatBotResponse(message.text)
                    ) : (
                      <div className={`text-sm ${message.sender === 'user' ? 'text-white' : 'text-gray-700'}`}>
                        {message.text}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Quick Actions */}
                {message.quickActions && (
                  <div className="mb-4 space-y-2">
                    {message.quickActions.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleQuickAction(action.query)}
                        className="block w-full text-left px-4 py-2 bg-white border border-indigo-200 rounded-lg text-sm text-indigo-700 hover:bg-indigo-50 hover:border-indigo-300 transition duration-150"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {isTyping && (
              <div className="text-left mb-4">
                <div className="inline-block p-4 rounded-2xl bg-white border border-gray-200 shadow-sm">
                  <div className="flex space-x-2 items-center">
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    <span className="text-xs text-gray-500 ml-2">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Chat input */}
          <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about medications..."
                className="flex-1 border border-gray-300 rounded-full py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
              />
              <button
                onClick={() => handleSend()}
                disabled={!inputValue.trim() || isTyping}
                className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-3 rounded-full hover:from-indigo-700 hover:to-purple-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed shadow-md transition duration-150"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">Press Enter to send</p>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl hover:scale-110 focus:outline-none transition duration-300 transform"
        >
          <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full animate-pulse"></span>
        </button>
      )}
    </div>
  );
};

export default ChatWidget;
