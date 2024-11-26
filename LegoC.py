import re
import tkinter as tk
from tkinter import messagebox, scrolledtext

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_pos = 0

    def tokenize(self):
        token_specs = [
            ('NUMBER', r'\d+(\.\d+)?'),  # Integer or float
            ('STRING', r'"[^"]*"'),     # String literal
            ('KEYWORD', r'\b(Base|Broke|Bubble|Build|Change|Con|Const|Create|Def|Destroy|Display|Do|Else|Elseif|False|Flip|For|Ifsnap|Link|Pane|Piece|Rebrick|Revoid|Set|Subs|True|While)\b'),  # Lego-C keywords
            ('OPERATOR', r'[+\-*/=<>!~&|]'),  # Operators
            ('IDENTIFIER', r'[a-z][a-zA-Z0-9_]{0,19}'),  # Identifiers
            ('NEWLINE', r'\n'),         # Newline
            ('SKIP', r'[ \t]+'),        # Whitespace
            ('COMMENT', r'##.*'),       # Single-line comments
        ]

        token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs)
        self.tokens = []

        for mo in re.finditer(token_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind in ('SKIP', 'COMMENT', 'NEWLINE'):
                continue
            self.tokens.append(Token(kind, value))

        return self.tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def parse(self):
        ast = []
        while self.current_token_index < len(self.tokens):
            statement = self.parse_statement()
            if statement is not None:
                ast.append(statement)
            else:
                # If no valid statement is found, move to the next token to prevent infinite loops.
                self.current_token_index += 1
        return ast

    def match(self, *expected_types):
        if self.current_token_index < len(self.tokens):
            current_token = self.tokens[self.current_token_index]
            if current_token.type in expected_types:
                self.current_token_index += 1
                return current_token
        return None

    def parse_statement(self):
        if self.current_token_index < len(self.tokens):
            if self.tokens[self.current_token_index].value == 'Display':
                return self.parse_display_statement()
            elif self.tokens[self.current_token_index].type == 'IDENTIFIER':
                return self.parse_assignment()
            elif self.tokens[self.current_token_index].value == 'Broke':
                self.match('KEYWORD')  # Consume 'Broke'
                return ('break_statement', None)
        return None

    def parse_display_statement(self):
        self.match('KEYWORD')  # Match 'Display'
        expression = self.parse_expression()
        if expression:
            return ('display_statement', expression)
        else:
            raise SyntaxError("Expected an expression after 'Display'.")

    def parse_assignment(self):
        identifier = self.match('IDENTIFIER')
        if not identifier:
            raise SyntaxError("Expected an identifier for assignment.")
        operator = self.match('OPERATOR')
        if not operator or operator.value != '=':
            raise SyntaxError("Expected '=' in assignment.")
        expression = self.parse_expression()
        if expression:
            return ('assignment', identifier.value, expression)
        else:
            raise SyntaxError("Expected an expression after '='.")

    def parse_expression(self):
        token = self.match('NUMBER', 'STRING', 'IDENTIFIER')
        if token:
            return token
        return None


class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}

    def interpret(self):
        output = []
        for node in self.ast:
            try:
                node_type = node[0]
                if node_type == 'display_statement':
                    value = self.evaluate_expression(node[1])
                    output.append(str(value))
                elif node_type == 'assignment':
                    var_name = node[1]
                    value = self.evaluate_expression(node[2])
                    self.variables[var_name] = value
                elif node_type == 'break_statement':
                    output.append("Break encountered.")
            except Exception as e:
                output.append(f"Error in execution: {str(e)}")
        return output

    def evaluate_expression(self, token):
        if token.type == 'NUMBER':
            return float(token.value)
        elif token.type == 'STRING':
            return token.value.strip('"')
        elif token.type == 'IDENTIFIER':
            return self.variables.get(token.value, None)
        return None

class CompilerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Lego-C Compiler")
        master.geometry("800x600")

        self.code_label = tk.Label(master, text="Enter Your Lego-C Code:")
        self.code_label.pack(pady=5)

        self.code_input = scrolledtext.ScrolledText(master, height=10, width=80)
        self.code_input.pack(pady=10)

        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.tokenize_btn = tk.Button(button_frame, text="Tokenize", command=self.tokenize_code)
        self.tokenize_btn.pack(side=tk.LEFT, padx=5)

        self.parse_btn = tk.Button(button_frame, text="Parse", command=self.parse_code)
        self.parse_btn.pack(side=tk.LEFT, padx=5)

        self.run_btn = tk.Button(button_frame, text="Run", command=self.run_code)
        self.run_btn.pack(side=tk.LEFT, padx=5)

        self.output_label = tk.Label(master, text="Output:")
        self.output_label.pack(pady=5)

        self.output = scrolledtext.ScrolledText(master, height=10, width=80)
        self.output.pack(pady=10)

    def tokenize_code(self):
        try:
            code = self.code_input.get("1.0", tk.END).strip()
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "Tokens:\n")
            for token in tokens:
                self.output.insert(tk.END, f"{token}\n")
        except Exception as e:
            messagebox.showerror("Tokenization Error", str(e))

    def parse_code(self):
        try:
            code = self.code_input.get("1.0", tk.END).strip()
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "Abstract Syntax Tree (AST):\n")
            for node in ast:
                self.output.insert(tk.END, f"{node}\n")
        except Exception as e:
            messagebox.showerror("Parsing Error", str(e))

    def run_code(self):
        try:
            code = self.code_input.get("1.0", tk.END).strip()
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            interpreter = Interpreter(ast)
            output = interpreter.interpret()
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "Program Output:\n")
            for line in output:
                self.output.insert(tk.END, f"{line}\n")
        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

def main():
    root = tk.Tk()
    compiler_gui = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
