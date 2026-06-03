from app.models.interview import InterviewPhase, ChatMessage, InterviewState

class InterviewFlowManager:
    PHASE_LIMITS = {
        InterviewPhase.INTRODUCTION: 3,
        InterviewPhase.TECHNICAL: 8,
        InterviewPhase.CRITICAL: 4,
        InterviewPhase.CLOSING: 2,
    }

    def check_phase_transition(self, state: InterviewState) -> bool:
        """Check if phase should transition based on exchange count and update state."""
        current_limit = self.PHASE_LIMITS.get(state.phase, 5)
        
        if state.exchange_count >= current_limit:
            if state.phase == InterviewPhase.INTRODUCTION:
                state.phase = InterviewPhase.TECHNICAL
            elif state.phase == InterviewPhase.TECHNICAL:
                state.phase = InterviewPhase.CRITICAL
            elif state.phase == InterviewPhase.CRITICAL:
                state.phase = InterviewPhase.CLOSING
            
            # Reset exchange count for new phase
            state.exchange_count = 0
            return True
        return False

    def get_phase_instructions(self, phase: InterviewPhase) -> str:
        """Get instructions specific to the current phase."""
        if phase == InterviewPhase.INTRODUCTION:
            return "This is the introduction phase. Keep it light, welcome the candidate, and ask a brief icebreaker."
        elif phase == InterviewPhase.TECHNICAL:
            return "This is the technical phase. Ask deep technical questions based on the candidate's resume."
        elif phase == InterviewPhase.CRITICAL:
            return "This is the critical thinking phase. Present a hypothetical scenario or architectural problem to solve based on their experience."
        elif phase == InterviewPhase.CLOSING:
            return "This is the closing phase. Ask if the candidate has any questions, and wrap up the interview gracefully."
        return ""

flow_manager = InterviewFlowManager()
