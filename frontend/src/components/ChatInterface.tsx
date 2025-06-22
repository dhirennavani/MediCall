import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Phone, Calendar, Clock, User, Bot, MicOff } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isTyping?: boolean;
}

interface ChatInterfaceProps {
  insuranceFile: File;
  onBack: () => void;
}

export default function ChatInterface({ insuranceFile, onBack }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: "Hi! I've processed your insurance card and I'm ready to help you book a medical appointment. What type of specialist or appointment are you looking for?",
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isAssistantTyping, setIsAssistantTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsAssistantTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "Great! I found several otolaryngologists in your network. Let me search for availability at 5pm. I'll call the clinics now to check their schedules.",
        "I'm calling Dr. Sarah Chen's ENT clinic now. They're in your insurance network and typically have evening appointments available.",
        "Perfect! I've successfully booked your appointment with Dr. Sarah Chen, ENT specialist, for tomorrow at 5:00 PM. The clinic is located at 123 Medical Plaza. You'll receive a confirmation text shortly."
      ];

      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: randomResponse,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsAssistantTyping(false);
    }, 2000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      // Simulate voice recording
      setTimeout(() => {
        setIsRecording(false);
        setInputValue("I want an appointment for an otolaryngologist at 5pm");
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={onBack}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
            >
              ←
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-teal-500 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-white font-semibold">MediCall AI Assistant</h1>
                <p className="text-sm text-slate-400">Ready to book your appointment</p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="px-3 py-1 bg-green-500/20 text-green-400 text-sm rounded-full border border-green-500/30">
              Insurance Verified
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`flex max-w-md ${
                  message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
                } items-start space-x-3`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user'
                      ? 'bg-blue-500 ml-3'
                      : 'bg-slate-600 mr-3'
                  }`}
                >
                  {message.type === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-teal-500 text-white'
                      : 'bg-slate-700/70 text-slate-100'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  <p
                    className={`text-xs mt-2 ${
                      message.type === 'user' ? 'text-blue-100' : 'text-slate-400'
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
          
          {isAssistantTyping && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-slate-700/70 rounded-2xl px-4 py-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-t border-slate-700/50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your appointment request... (e.g., 'I want an appointment for an otolaryngologist at 5pm')"
                className="w-full bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-3 pr-12 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[52px] max-h-32"
                rows={1}
              />
            </div>
            
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-xl transition-all duration-300 ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white'
              }`}
            >
              {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
            
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim()}
              className="p-3 bg-gradient-to-r from-blue-500 to-teal-500 text-white rounded-xl hover:from-blue-600 hover:to-teal-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          {isRecording && (
            <div className="mt-3 flex items-center justify-center space-x-2 text-red-400">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm">Recording... Speak now</span>
            </div>
          )}
          
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              onClick={() => setInputValue("I need to see an otolaryngologist for my ear problem")}
              className="px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 text-sm rounded-lg transition-colors"
            >
              ENT Specialist
            </button>
            <button
              onClick={() => setInputValue("I want a dermatology appointment for skin issues")}
              className="px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 text-sm rounded-lg transition-colors"
            >
              Dermatologist
            </button>
            <button
              onClick={() => setInputValue("Book me an orthopedist for knee pain")}
              className="px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 text-sm rounded-lg transition-colors"
            >
              Orthopedist
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}