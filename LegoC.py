import tkinter as tk
from tkinter import scrolledtext

# Enum-like class for Token Types
class TokenType:
    KEYWORD = 'KEYWORD'
    IDENTIFIER = 'IDENTIFIER'
    INTEGER_LITERAL = 'Linklit'
    FLOAT_LITERAL = 'Bubblelit'
    STRING_LITERAL = 'Piecelit'
    OPERATOR = 'OPERATOR'
    PUNCTUATOR = 'PUNCTUATOR'
    SPACE = 'SPACE'  # Added SPACE type
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
            "Rebrick": TokenType.KEYWORD,
            "Broke": TokenType.KEYWORD,
            "Change": TokenType.KEYWORD,
            "Con": TokenType.KEYWORD,
            "Const": TokenType.KEYWORD,
            "Create": TokenType.KEYWORD,
            "Def": TokenType.KEYWORD,
            "Do": TokenType.KEYWORD,
            "Flip": TokenType.KEYWORD,
            "Ifsnap": TokenType.KEYWORD,
            "Piece": TokenType.KEYWORD,
            "Put": TokenType.KEYWORD,
            "Revoid": TokenType.KEYWORD,
            "Stable": TokenType.KEYWORD,
            "Set": TokenType.KEYWORD,
            "Snap": TokenType.KEYWORD,
            "Snapif": TokenType.KEYWORD,
            "Subs": TokenType.KEYWORD,
            "While": TokenType.KEYWORD,
            "Wobble": TokenType.KEYWORD
        }

    def is_whitespace(self, c):
        return c in (' ', '\t', '\n', '\r')

    def is_alpha(self, c):
        return c.isalpha()

    def is_digit(self, c):
        return c.isdigit()

    def is_alphanumeric(self, c):
        return c.isalnum()

    def is_underscore(self, c):
        return c == "_"

    def get_next_word(self):
        start = self.position
        while self.position < len(self.input) and (self.is_alphanumeric(self.input[self.position]) or self.is_underscore(self.input[self.position])):
            self.position += 1
        return self.input[start:self.position]

    def get_next_number(self):
        start = self.position
        while self.position < len(self.input) and (self.input[self.position].isdigit() or self.input[self.position] == '.'):
            self.position += 1
        return self.input[start:self.position]

    def tokenize(self):
        tokens = []
        lexemes = []
        errors = []

        while self.position < len(self.input):
            current_char = self.input[self.position]

            if current_char == ' ':
                tokens.append(Token(TokenType.SPACE, "space"))
                lexemes.append("")
                self.position += 1
                continue

            if self.is_whitespace(current_char):
                self.position += 1
                continue

            if self.is_alpha(current_char):
                word = self.get_next_word()
                if word in self.keywords:
                    tokens.append(Token(TokenType.KEYWORD, word))
                    lexemes.append(word)
                else:
                    if any(c.isupper() for c in word):
                        errors.append(f"Lexical Error: '{word}' is undefined")
                    tokens.append(Token(TokenType.IDENTIFIER, word))
                    lexemes.append(word)

            elif self.is_digit(current_char):
                number = self.get_next_number()
                if '.' in number:
                    tokens.append(Token(TokenType.FLOAT_LITERAL, number))
                else:
                    tokens.append(Token(TokenType.INTEGER_LITERAL, number))
                lexemes.append(number)

            elif current_char == '"':
                start = self.position
                self.position += 1
                while self.position < len(self.input) and self.input[self.position] != '"':
                    self.position += 1
                if self.position >= len(self.input):
                    errors.append(f"Missing closing quote for string starting at position {start}")
                    tokens.append(Token(TokenType.UNKNOWN, self.input[start:]))
                else:
                    self.position += 1
                    tokens.append(Token(TokenType.STRING_LITERAL, self.input[start:self.position]))
                lexemes.append(self.input[start:self.position])

            elif current_char in ('+', '-', '*', '/'):
                tokens.append(Token(TokenType.OPERATOR, current_char))
                lexemes.append(current_char)
                self.position += 1

            elif current_char in ('(', ')', '{', '}', ';'):
                tokens.append(Token(TokenType.PUNCTUATOR, current_char))
                lexemes.append(current_char)
                self.position += 1

            else:
                errors.append(f"Unrecognized character '{current_char}' at position {self.position}")
                tokens.append(Token(TokenType.UNKNOWN, current_char))
                lexemes.append(current_char)
                self.position += 1

        return tokens, lexemes, errors

# GUI components and functions
class TextWithLineNumbers(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.line_numbers = tk.Text(self, width=4, padx=3, takefocus=0, border=0, background="lightgray", state="disabled", wrap="none")
        self.line_numbers.pack(side="left", fill="y")

        self.text = scrolledtext.ScrolledText(self, wrap="none")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<KeyPress>", self._update_line_numbers)
        self.text.bind("<MouseWheel>", self._update_line_numbers)
        self.text.bind("<ButtonRelease>", self._update_line_numbers)
        self.text.bind("<Configure>", self._update_line_numbers)

    def _update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")

        lines = self.text.index("end-1c").split(".")[0]
        line_numbers = "\n".join(str(i) for i in range(1, int(lines) + 1))
        self.line_numbers.insert("1.0", line_numbers)

        self.line_numbers.config(state="disabled")
        self.line_numbers.yview_moveto(self.text.yview()[0])

def update_analysis(event=None):
    source_code = text_with_line_numbers.text.get("1.0", "end-1c")
    lexer = LexicalAnalyzer(source_code)
    tokens, lexemes, errors = lexer.tokenize()
    
    lexeme_text.delete("1.0", "end-1c")
    token_text.delete("1.0", "end-1c")
    error_text.delete("1.0", "end-1c")
    program_text.delete("1.0", "end-1c")
    
    for token, lexeme in zip(tokens, lexemes):
        lexeme_text.insert(tk.END, f"{lexeme}\n")
        token_text.insert(tk.END, f"{token.type}\n")
    
    if errors:
        for error in errors:
            error_text.insert(tk.END, f"{error}\n")
    else:
        error_text.insert(tk.END, "No errors detected.\n")
        program_text.insert(tk.END, "Program output is ready for display.\n")

root = tk.Tk()
root.title("Lego-C Code Analyzer")

input_frame = tk.Frame(root)
input_frame.pack(fill=tk.BOTH, pady=5)

label = tk.Label(input_frame, text="Enter Lego-C code:")
label.pack(side="top", anchor="w")

text_with_line_numbers = TextWithLineNumbers(input_frame)
text_with_line_numbers.pack(side="top", fill="both", expand=True, padx=5, pady=5)

output_frame = tk.Frame(root)
output_frame.pack(fill=tk.BOTH, pady=5)

lexeme_label = tk.Label(output_frame, text="Lexemes:")
lexeme_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

lexeme_text = tk.Text(output_frame, width=25, height=10)
lexeme_text.grid(row=1, column=0, padx=5, pady=5)

token_label = tk.Label(output_frame, text="Tokens:")
token_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

token_text = tk.Text(output_frame, width=25, height=10)
token_text.grid(row=1, column=1, padx=5, pady=5)

error_label = tk.Label(output_frame, text="Errors:")
error_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

error_text = tk.Text(output_frame, width=35, height=10)
error_text.grid(row=1, column=2, padx=5, pady=5)

program_label = tk.Label(output_frame, text="Program:")
program_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")

program_text = tk.Text(output_frame, width=35, height=10)
program_text.grid(row=1, column=3, padx=5, pady=5)

text_with_line_numbers.text.bind("<KeyRelease>", update_analysis)

root.mainloop()
