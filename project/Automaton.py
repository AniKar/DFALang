# Deterministic finite automaton

class Automaton:
    def __init__(self, state_count, alphabet, transitions, accept_states):
        # take the start state be always 1
        self.start_state = 1
        self.state_count = state_count
        self.alphabet = alphabet
        self.transitions = transitions
        self.accept_states = accept_states

    # get the next state from the given state with the given input
    def __nextState(self, current_state, input):
        return self.transitions.get((current_state, input), None)

    # check if the given state is an accept state
    def __inAcceptStates(self, current_state):
        return current_state in self.accept_states

    # accept a string from the given state
    def __acceptsStringFromState(self, current_state, input_str):
        if not input_str:
            return self.__inAcceptStates(current_state)

        next_state = self.__nextState(current_state, input_str[0])
        return next_state and self.__acceptsStringFromState(next_state, input_str[1:])

    # accept a string from the initial state
    def acceptsString(self, input_str):
        return self.__acceptsStringFromState(self.start_state, input_str)

    # automaton string representation
    def __str__(self):
        s = "{\n" \
            " State count = "  + str(self.state_count) + "\n" \
            " Alphabet = " + str(self.alphabet) + "\n" \
            " Transitions = " + str(self.transitions) + "\n" \
            " Accept States = " + str(self.accept_states) + "\n" \
            "}"
        return s

    # check for correct automaton definition
    def check(self):
        return self.__checkTransitions() \
           and self.__checkAcceptStates()

    # check for correct transition list definition
    def __checkTransitions(self):
        for state_input, next_state  in self.transitions.items():
            if not self.__checkTransition(state_input[0], state_input[1], next_state):
                return False
        return True

    # check for correctness of a single transition
    def __checkTransition(self, state1, input, state2):
        return self.__validState(state1) \
           and self.__validState(state2) \
           and self.__validInput(input)

    # check for correct accept states definition
    def __checkAcceptStates(self):
        for s in self.accept_states:
            if not self.__validState(s):
                return False
        return True

    # check for a valid state number
    def __validState(self, s):
        return (s in range(1, self.state_count + 1))

    # check for a valid input
    def __validInput(self, input):
        return input in self.alphabet
