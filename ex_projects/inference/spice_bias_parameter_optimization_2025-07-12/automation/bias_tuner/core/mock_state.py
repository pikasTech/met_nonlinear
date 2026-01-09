"""
Mock state management for bias tuner testing.
Provides enum-based state management with validation.
"""

from enum import Enum
from typing import Optional, Set


class MockState(Enum):
    """Mock mode states representing different compensation stages."""
    BASELINE = "baseline"
    LAYER1 = "layer1"
    LAYER12 = "layer12"
    LAYER123 = "layer123"
    
    @classmethod
    def from_string(cls, value: str) -> 'MockState':
        """
        Create MockState from string value.
        
        Args:
            value: String representation of state
            
        Returns:
            MockState enum value
            
        Raises:
            ValueError: If value is not a valid state
        """
        try:
            return cls(value)
        except ValueError:
            valid_states = [s.value for s in cls]
            raise ValueError(
                f"Invalid mock state: '{value}'. "
                f"Valid states are: {valid_states}"
            )
    
    @classmethod
    def get_valid_transitions(cls) -> dict:
        """
        Get valid state transitions.
        
        Returns:
            Dict mapping each state to set of valid next states
        """
        return {
            cls.BASELINE: {cls.LAYER1},
            cls.LAYER1: {cls.LAYER12},
            cls.LAYER12: {cls.LAYER123},
            cls.LAYER123: set()  # Terminal state
        }
    
    @classmethod
    def validate_transition(cls, from_state: 'MockState', to_state: 'MockState') -> bool:
        """
        Validate if transition from one state to another is allowed.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = cls.get_valid_transitions()
        valid_next_states = valid_transitions.get(from_state, set())
        return to_state in valid_next_states
    
    def get_error_analysis_file(self) -> str:
        """
        Get the error analysis filename for this state.
        
        Returns:
            Filename for error analysis JSON
        """
        return f"error_analysis_{self.value}.json"
    
    def get_compensated_layers(self) -> list:
        """
        Get list of layers that should be compensated in this state.
        
        Returns:
            List of layer indices
        """
        layer_map = {
            MockState.BASELINE: [],
            MockState.LAYER1: [1],
            MockState.LAYER12: [1, 2],
            MockState.LAYER123: [1, 2, 3]
        }
        return layer_map[self]
    
    def __str__(self) -> str:
        """String representation."""
        return self.value