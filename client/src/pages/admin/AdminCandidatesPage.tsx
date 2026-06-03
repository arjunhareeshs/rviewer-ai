import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Send, Filter, ChevronRight, X } from "lucide-react";

export default function AdminPage() {
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { role: 'ai', content: '9 candidates found in the database.' }
  ]);
  const [shortlist, setShortlist] = useState<string[]>([]);

  const mockCandidates = [
    { id: '1', name: 'Arjun S', overall: 79, ats: 74, interview: 82, skills: ['PyTorch', 'Docker'] },
    { id: '2', name: 'Varun S', overall: 67, ats: 62, interview: 71, skills: ['TF', 'NumPy', 'Pandas'] },
  ];

  const handleChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setChatHistory([...chatHistory, { role: 'user', content: chatInput }]);
    setTimeout(() => {
      setChatHistory(prev => [...prev, { role: 'ai', content: 'Filtered based on your request. 6 remain.' }]);
    }, 600);
    setChatInput("");
  };

  const toggleShortlist = (id: string) => {
    setShortlist(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  return (
    <div className="flex h-screen w-full bg-cream">
      
      {/* LEFT PANEL - Resume Viewer */}
      <div className="w-1/2 border-r border-border bg-surface flex flex-col relative z-10 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
        <div className="flex-1 overflow-y-auto p-6 flex flex-col">
          {!selectedCandidate ? (
            <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-border rounded-2xl bg-cream m-4 hover:border-accent transition-colors">
               <div className="w-16 h-16 bg-accent-soft rounded-full flex items-center justify-center text-accent mb-4">
                 <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
               </div>
               <p className="font-bold text-text-primary text-lg">Select a candidate</p>
               <p className="text-sm text-text-secondary mt-1">Their profile will appear here</p>
            </div>
          ) : (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 max-w-xl mx-auto py-6 w-full">
               <div className="flex justify-between items-start mb-6">
                 <div>
                   <h2 className="font-display text-3xl font-bold text-text-primary">{selectedCandidate.name}</h2>
                   <p className="text-sm font-medium text-text-secondary mt-1">varun@example.com · +91 9876543210</p>
                 </div>
                 <button onClick={() => setSelectedCandidate(null)} className="p-2 hover:bg-cream rounded-full text-text-muted hover:text-text-primary transition-colors">
                   <X size={20} />
                 </button>
               </div>

               <div className="grid grid-cols-3 gap-4">
                 <div className="bg-cream p-4 rounded-xl border border-border shadow-sm text-center">
                   <p className="text-xs font-bold text-text-secondary uppercase tracking-wider mb-1">Overall</p>
                   <p className="font-mono text-2xl font-bold text-text-primary">{selectedCandidate.overall}</p>
                 </div>
                 <div className="bg-cream p-4 rounded-xl border border-border shadow-sm text-center">
                   <p className="text-xs font-bold text-text-secondary uppercase tracking-wider mb-1">ATS Score</p>
                   <p className="font-mono text-2xl font-bold text-text-primary">{selectedCandidate.ats}</p>
                 </div>
                 <div className="bg-cream p-4 rounded-xl border border-border shadow-sm text-center">
                   <p className="text-xs font-bold text-text-secondary uppercase tracking-wider mb-1">Interview</p>
                   <p className="font-mono text-2xl font-bold text-success">{selectedCandidate.interview}</p>
                 </div>
               </div>

               <div className="bg-cream p-6 rounded-2xl border border-border shadow-sm mt-6">
                 <h3 className="text-sm font-bold uppercase tracking-widest text-text-primary mb-3">Extracted Skills</h3>
                 <div className="flex flex-wrap gap-2">
                   {selectedCandidate.skills.map((s: string) => <span key={s} className="bg-surface border border-border text-text-primary font-semibold px-3 py-1 rounded-md text-sm">{s}</span>)}
                 </div>
               </div>
            </motion.div>
          )}
        </div>
        
        {/* Shortlist Bar */}
        <div className="flex-none p-4 bg-surface border-t border-border flex justify-between items-center shadow-[0_-4px_24px_rgba(0,0,0,0.05)] z-20">
          <span className="font-bold text-text-primary">Shortlisted: <span className="text-accent">{shortlist.length}</span></span>
          <button 
            disabled={shortlist.length < 2}
            className="px-6 py-2 bg-text-primary hover:bg-text-primary/90 disabled:bg-text-primary/50 text-white font-bold rounded-lg transition-colors text-sm shadow-sm"
          >
            Compare Selected
          </button>
        </div>
      </div>

      {/* RIGHT PANEL - Search & Filter */}
      <div className="w-1/2 flex flex-col bg-cream">
        
        {/* Top Search */}
        <div className="p-4 border-b border-border bg-surface">
          <div className="relative">
             <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={18} />
             <input type="text" placeholder="Search candidates..." className="w-full pl-10 pr-4 py-3 bg-cream border border-border rounded-xl text-sm font-medium focus:ring-1 focus:ring-accent outline-none transition-colors" />
          </div>
        </div>

        <div className="flex-1 flex flex-col min-h-0">
          {/* AI Filter Chat */}
          <div className="flex-none border-b border-border bg-accent-soft p-4">
             <div className="flex items-center gap-2 mb-3">
               <div className="w-6 h-6 bg-accent rounded text-white flex items-center justify-center text-xs">✨</div>
               <span className="font-bold text-text-primary text-sm">AI Filter Chat</span>
             </div>
             <div className="space-y-3 mb-4 max-h-40 overflow-y-auto text-sm font-medium pr-2">
               {chatHistory.map((msg, i) => (
                 <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                   <div className={`px-4 py-2 rounded-2xl max-w-[80%] ${msg.role === 'user' ? 'bg-accent text-white rounded-br-sm' : 'bg-surface border border-border text-text-primary rounded-bl-sm shadow-sm'}`}>
                     {msg.content}
                   </div>
                 </div>
               ))}
             </div>
             <form onSubmit={handleChat} className="flex gap-2">
               <input 
                 type="text" 
                 value={chatInput}
                 onChange={e => setChatInput(e.target.value)}
                 placeholder="Type a filter (e.g. 'show python devs with ATS > 70')" 
                 className="flex-1 bg-surface border border-border rounded-xl px-4 py-2 text-sm font-medium focus:ring-1 focus:ring-accent outline-none transition-colors" 
               />
               <button type="submit" className="p-2.5 bg-accent text-white rounded-xl hover:bg-accent/90 transition-colors shadow-sm"><Send size={16}/></button>
             </form>
          </div>

          {/* Quick Filters */}
          <div className="flex-none p-3 border-b border-border flex gap-2 overflow-x-auto bg-surface">
            <Filter size={14} className="text-text-muted mt-1 mr-1" />
            {['Interview Done', 'ATS > 70', 'Has Intern'].map(f => (
              <button key={f} className="px-3 py-1 bg-cream border border-border rounded-full text-xs font-bold text-text-secondary hover:text-text-primary hover:border-accent whitespace-nowrap transition-colors">{f}</button>
            ))}
          </div>

          {/* Results Grid */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
             {mockCandidates.map(c => (
               <div key={c.id} className="bg-surface border border-border rounded-xl p-4 hover:border-accent hover:shadow-md transition-all group">
                 <div className="flex justify-between items-start mb-2">
                   <div>
                     <h3 className="font-bold text-text-primary text-lg">{c.name}</h3>
                     <div className="flex gap-1 mt-1">
                       {c.skills.map(s => <span key={s} className="text-[10px] uppercase tracking-wider font-bold bg-cream text-text-secondary border border-border px-2 py-0.5 rounded">{s}</span>)}
                     </div>
                   </div>
                   <div className="text-right">
                     <p className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">Overall</p>
                     <p className="font-mono text-xl font-bold text-text-primary">{c.overall}</p>
                   </div>
                 </div>
                 <div className="flex gap-4 text-xs font-semibold text-text-secondary mb-4">
                   <span>ATS: <span className="text-text-primary font-bold">{c.ats}</span></span>
                   <span>Interview: <span className="text-success font-bold">✅ {c.interview}</span></span>
                 </div>
                 <div className="flex gap-2">
                   <button 
                     onClick={() => setSelectedCandidate(c)}
                     className="flex-1 py-1.5 border border-border rounded-lg text-xs font-bold text-text-primary hover:bg-cream hover:border-accent hover:text-accent transition-colors flex justify-center items-center gap-1"
                   >
                     View Resume <ChevronRight size={14}/>
                   </button>
                   <button 
                     onClick={() => toggleShortlist(c.id)}
                     className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-colors ${shortlist.includes(c.id) ? 'bg-accent-soft border-accent/20 text-accent' : 'bg-surface border-border text-text-secondary hover:border-text-primary hover:text-text-primary'}`}
                   >
                     {shortlist.includes(c.id) ? '✓ Shortlisted' : '+ Shortlist'}
                   </button>
                 </div>
               </div>
             ))}
          </div>

        </div>
      </div>
      
    </div>
  );
}
