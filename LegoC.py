import tkinter as tk
from tkinter import scrolledtext

# Enum-like class for Token Types
class TokenType:
    KEYWORD = 'KEYWORD'
    IDENTIFIER = 'IDENTIFIER'
    INTEGER_LITERAL = 'INTEGER_LITERAL'
    FLOAT_LITERAL = 'FLOAT_LITERAL'
    STRING_LITERAL = 'STRING_LITERAL'
    OPERATOR = 'OPERATOR'
    PUNCTUATOR = 'PUNCTUATOR'
    UNKNOWN = 'UNKNOWN'


# Token class to hold the token type and value
class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value


# LexicalAnalyzer class to tokenize the input source code
class LexicalAnalyzer:
    def __init__(self, source_code):
        self.input = source_code
        self.position = 0
        self.keywords = {
            "Build": TokenType.KEYWORD,
            "Destroy": TokenType.KEYWORD,
            "Pane": TokenType.KEYWORD,
            "Link": TokenType.KEYWORD,
            "Display": TokenType.KEYWORD,
            "Rebrick": TokenType.KEYWORD
        }

    def is_whitespace(self, c):
        return c in (' ', '\t', '\n', '\r')

    def is_alpha(self, c):
        return c.isalpha()

    def is_digit(self, c):
        return c.isdigit()

    def is_alphanumeric(self, c):
        return c.isalnum()

    def get_next_word(self):
        start = self.position
        while self.position < len(self.input) and self.is_alphanumeric(self.input[self.position]):
            self.position += 1
        return self.input[start:self.position]

    def get_next_number(self):
        start = self.position
        has_decimal = False
        while self.position < len(self.input) and (self.is_digit(self.input[self.position]) or self.input[self.position] == '.'):
            if self.input[self.position] == '.':
                if has_decimal:
                    break
                has_decimal = True
            self.position += 1
        return self.input[start:self.position]

    def tokenize(self):
        tokens = []
        self.position = 0  # Reset position for each analysis

        while self.position < len(self.input):
            current_char = self.input[self.position]

            if self.is_whitespace(current_char):
                self.position += 1
                continue

            if self.is_alpha(current_char):
                word = self.get_next_word()
                if word in self.keywords:
                    tokens.append(Token(TokenType.KEYWORD, word))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, word))

            elif self.is_digit(current_char):
                number = self.get_next_number()
                if '.' in number:
                    tokens.append(Token(TokenType.FLOAT_LITERAL, number))
                else:
                    tokens.append(Token(TokenType.INTEGER_LITERAL, number))

            elif current_char == '"':  # Start of a string literal
                start = self.position
                self.position += 1
                while self.position < len(self.input) and self.input[self.position] != '"':
                    self.position += 1
                if self.position >= len(self.input):  # Missing closing quote
                    tokens.append(Token(TokenType.UNKNOWN, self.input[start:]))
                else:
                    self.position += 1  # Include the closing quote
                    tokens.append(Token(TokenType.STRING_LITERAL, self.input[start:self.position]))

            elif current_char in ('+', '-', '*', '/'):
                tokens.append(Token(TokenType.OPERATOR, current_char))
                self.position += 1

            elif current_char in ('(', ')', '{', '}', ';'):
                tokens.append(Token(TokenType.PUNCTUATOR, current_char))
                self.position += 1

            else:
                tokens.append(Token(TokenType.UNKNOWN, current_char))
                self.position += 1

        return tokens


# Error detection functions
def validate_operator_placement(tokens):
    errors = []
    for i, token in enumerate(tokens):
        if token.type == TokenType.OPERATOR:
            if i == 0 or i == len(tokens) - 1 or \
               (tokens[i - 1].type not in {TokenType.IDENTIFIER, TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL} or
                tokens[i + 1].type not in {TokenType.IDENTIFIER, TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL}):
                errors.append(f"Invalid operator placement near '{token.value}' at position {i}.")
    return errors

def validate_return_value(tokens):
    errors = []
    for i, token in enumerate(tokens):
        if token.type == TokenType.KEYWORD and token.value == "Rebrick":
            if i == len(tokens) - 1 or tokens[i + 1].type not in {TokenType.INTEGER_LITERAL, TokenType.IDENTIFIER}:
                errors.append(f"Invalid return value after 'Rebrick' at position {i}.")
    return errors

def validate_closing_quotes(tokens):
    errors = []
    for token in tokens:
        if token.type == TokenType.UNKNOWN and '"' in token.value:
            errors.append(f"Missing closing quote in string: {token.value}")
    return errors


# GUI functions
def update_analysis(event=None):
    source_code = text_input.get("1.0", "end-1c")
    lexer = LexicalAnalyzer(source_code)
    tokens = lexer.tokenize()

    # Clear the panes
    lexeme_text.delete("1.0", "end")
    token_text.delete("1.0", "end")
    error_text.delete("1.0", "end")
    program_text.delete("1.0", "end")

    # Display lexemes and tokens
    for token in tokens:
        lexeme_text.insert(tk.END, f"{token.value}\n")
        token_text.insert(tk.END, f"{token.type}: {token.value}\n")

    # Validate tokens and display errors
    errors = []
    errors.extend(validate_operator_placement(tokens))
    errors.extend(validate_return_value(tokens))
    errors.extend(validate_closing_quotes(tokens))

    if errors:
        for error in errors:
            error_text.insert(tk.END, error + "\n")
    else:
        error_text.insert(tk.END, "No errors detected.\n")
        program_text.insert(tk.END, "Program executed successfully.\n")


# Set up the GUI window
root = tk.Tk()
root.title("Lego-C Compiler")

# Frames for layout
input_frame = tk.Frame(root)
input_frame.pack(fill=tk.BOTH, pady=5)

output_frame = tk.Frame(root)
output_frame.pack(fill=tk.BOTH, expand=True)

analysis_frame = tk.Frame(root)
analysis_frame.pack(fill=tk.BOTH, expand=True)

# Input pane
label = tk.Label(input_frame, text="Enter Your Lego-C Code:")
label.pack(anchor=tk.W, pady=5)

text_input = scrolledtext.ScrolledText(input_frame, width=80, height=10)
text_input.pack(padx=5, pady=5, fill=tk.BOTH)
text_input.bind("<KeyRelease>", update_analysis)

# Lexemes and Tokens (Left Side)
left_frame = tk.Frame(analysis_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

lexeme_label = tk.Label(left_frame, text="Lexemes:")
lexeme_label.pack(anchor=tk.W, pady=5)

lexeme_text = scrolledtext.ScrolledText(left_frame, width=40, height=15)
lexeme_text.pack(padx=5, pady=5, fill=tk.BOTH)

token_label = tk.Label(left_frame, text="Tokens:")
token_label.pack(anchor=tk.W, pady=5)

token_text = scrolledtext.ScrolledText(left_frame, width=40, height=15)
token_text.pack(padx=5, pady=5, fill=tk.BOTH)

# Errors and Program Output (Right Side)
right_frame = tk.Frame(analysis_frame)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

error_label = tk.Label(right_frame, text="Errors:")
error_label.pack(anchor=tk.W, pady=5)

error_text = scrolledtext.ScrolledText(right_frame, width=40, height=15)
error_text.pack(padx=5, pady=5, fill=tk.BOTH)

program_label = tk.Label(right_frame, text="Program:")
program_label.pack(anchor=tk.W, pady=5)

program_text = scrolledtext.ScrolledText(right_frame, width=40, height=15)
program_text.pack(padx=5, pady=5, fill=tk.BOTH)

# Run the tkinter main loop
root.mainloop()
