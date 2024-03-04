import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import csv

class Tarefa:
    def __init__(self, id, titulo, descricao, prioridade, data_limite, concluida=False):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.prioridade = prioridade
        self.data_limite = data_limite
        self.concluida = concluida

class AplicativoGerenciadorTarefas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Tarefas")
        self.geometry("800x600")

        self.tarefas = []
        self.carregar_tarefas_do_banco_de_dados()

        self.criar_widgets()
        self.popular_tarefas()

        self.verificar_lembretes()

    def criar_widgets(self):
        self.frame_tarefa = ttk.Frame(self)
        self.frame_tarefa.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree_tarefa = ttk.Treeview(self.frame_tarefa, columns=("Título", "Descrição", "Prioridade", "Data Limite", "Concluída"), show="headings")
        self.tree_tarefa.heading("Título", text="Título")
        self.tree_tarefa.heading("Descrição", text="Descrição")
        self.tree_tarefa.heading("Prioridade", text="Prioridade")
        self.tree_tarefa.heading("Data Limite", text="Data Limite")
        self.tree_tarefa.heading("Concluída", text="Concluída")
        self.tree_tarefa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_tarefa = ttk.Scrollbar(self.frame_tarefa, orient="vertical", command=self.tree_tarefa.yview)
        self.scroll_tarefa.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_tarefa.configure(yscrollcommand=self.scroll_tarefa.set)

        self.botao_adicionar = ttk.Button(self, text="Adicionar Tarefa", command=self.adicionar_tarefa)
        self.botao_adicionar.pack(pady=5)

        self.botao_editar = ttk.Button(self, text="Editar Tarefa", command=self.editar_tarefa)
        self.botao_editar.pack(pady=5)

        self.botao_remover = ttk.Button(self, text="Remover Tarefa", command=self.remover_tarefa)
        self.botao_remover.pack(pady=5)

        self.botao_marcar_concluida = ttk.Button(self, text="Marcar como Concluída", command=self.marcar_concluida)
        self.botao_marcar_concluida.pack(pady=5)

        self.criar_filtros()
        self.criar_ordenacao()

    def popular_tarefas(self, tarefas=None):
        if tarefas is None:
            tarefas = self.tarefas

        self.tree_tarefa.delete(*self.tree_tarefa.get_children())
        for tarefa in tarefas:
            self.tree_tarefa.insert("", "end", text=tarefa.id, values=(tarefa.titulo, tarefa.descricao, tarefa.prioridade, tarefa.data_limite, "Sim" if tarefa.concluida else "Não"))

    def adicionar_tarefa(self):
        self.janela_adicionar_tarefa = tk.Toplevel(self)
        self.janela_adicionar_tarefa.title("Adicionar Tarefa")

        self.label_titulo = ttk.Label(self.janela_adicionar_tarefa, text="Título:")
        self.label_titulo.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_titulo = ttk.Entry(self.janela_adicionar_tarefa)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5)

        self.label_descricao = ttk.Label(self.janela_adicionar_tarefa, text="Descrição:")
        self.label_descricao.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_descricao = ttk.Entry(self.janela_adicionar_tarefa)
        self.entry_descricao.grid(row=1, column=1, padx=5, pady=5)

        self.label_prioridade = ttk.Label(self.janela_adicionar_tarefa, text="Prioridade:")
        self.label_prioridade.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_prioridade = ttk.Entry(self.janela_adicionar_tarefa)
        self.entry_prioridade.grid(row=2, column=1, padx=5, pady=5)

        self.label_data_limite = ttk.Label(self.janela_adicionar_tarefa, text="Data Limite (AAAA-MM-DD):")
        self.label_data_limite.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_data_limite = ttk.Entry(self.janela_adicionar_tarefa)
        self.entry_data_limite.grid(row=3, column=1, padx=5, pady=5)

        self.botao_adicionar_tarefa = ttk.Button(self.janela_adicionar_tarefa, text="Adicionar Tarefa", command=self.salvar_tarefa)
        self.botao_adicionar_tarefa.grid(row=4, columnspan=2, padx=5, pady=5)
    def salvar_tarefa(self):
        titulo = self.entry_titulo.get()
        descricao = self.entry_descricao.get()
        prioridade = self.entry_prioridade.get()
        data_limite = self.entry_data_limite.get()

        # Validando dados
        if not titulo or not prioridade or not data_limite:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")
            return

        try:
            data_limite = datetime.strptime(data_limite, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Por favor, use AAAA-MM-DD.")
            return

        id_tarefa = len(self.tarefas) + 1
        nova_tarefa = Tarefa(id_tarefa, titulo, descricao, prioridade, data_limite)
        self.tarefas.append(nova_tarefa)
        self.salvar_tarefas_no_banco_de_dados()  
        self.popular_tarefas()
        self.janela_adicionar_tarefa.destroy()

    def editar_tarefa(self):
        item_selecionado = self.tree_tarefa.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Por favor, selecione uma tarefa para editar.")
            return

        id_tarefa = int(self.tree_tarefa.item(item_selecionado, "text"))
        for tarefa in self.tarefas:
            if tarefa.id == id_tarefa:
                self.janela_editar_tarefa = tk.Toplevel(self)
                self.janela_editar_tarefa.title("Editar Tarefa")

                self.label_titulo = ttk.Label(self.janela_editar_tarefa, text="Título:")
                self.label_titulo.grid(row=0, column=0, padx=5, pady=5, sticky="e")
                self.entry_titulo = ttk.Entry(self.janela_editar_tarefa)
                self.entry_titulo.insert(0, tarefa.titulo)
                self.entry_titulo.grid(row=0, column=1, padx=5, pady=5)

                self.label_descricao = ttk.Label(self.janela_editar_tarefa, text="Descrição:")
                self.label_descricao.grid(row=1, column=0, padx=5, pady=5, sticky="e")
                self.entry_descricao = ttk.Entry(self.janela_editar_tarefa)
                self.entry_descricao.insert(0, tarefa.descricao)
                self.entry_descricao.grid(row=1, column=1, padx=5, pady=5)

                self.label_prioridade = ttk.Label(self.janela_editar_tarefa, text="Prioridade:")
                self.label_prioridade.grid(row=2, column=0, padx=5, pady=5, sticky="e")
                self.entry_prioridade = ttk.Entry(self.janela_editar_tarefa)
                self.entry_prioridade.insert(0, tarefa.prioridade)
                self.entry_prioridade.grid(row=2, column=1, padx=5, pady=5)

                self.label_data_limite = ttk.Label(self.janela_editar_tarefa, text="Data Limite (AAAA-MM-DD):")
                self.label_data_limite.grid(row=3, column=0, padx=5, pady=5, sticky="e")
                self.entry_data_limite = ttk.Entry(self.janela_editar_tarefa)
                self.entry_data_limite.insert(0, str(tarefa.data_limite))
                self.entry_data_limite.grid(row=3, column=1, padx=5, pady=5)

                self.botao_editar_tarefa = ttk.Button(self.janela_editar_tarefa, text="Salvar Alterações", command=lambda: self.salvar_tarefa_editada(tarefa))
                self.botao_editar_tarefa.grid(row=4, columnspan=2, padx=5, pady=5)
                break

    def salvar_tarefa_editada(self, tarefa):
        titulo = self.entry_titulo.get()
        descricao = self.entry_descricao.get()
        prioridade = self.entry_prioridade.get()
        data_limite = self.entry_data_limite.get()

        # Validando dados
        if not titulo or not prioridade or not data_limite:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")
            return

        try:
            data_limite = datetime.strptime(data_limite, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Por favor, use AAAA-MM-DD.")
            return

        tarefa.titulo = titulo
        tarefa.descricao = descricao
        tarefa.prioridade = prioridade
        tarefa.data_limite = data_limite

        self.salvar_tarefas_no_banco_de_dados() 
        self.popular_tarefas()
        self.janela_editar_tarefa.destroy()

    def remover_tarefa(self):
        item_selecionado = self.tree_tarefa.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Por favor, selecione uma tarefa para remover.")
            return

        confirmado = messagebox.askyesno("Confirmar Remoção", "Tem certeza de que deseja remover esta tarefa?")
        if confirmado:
            id_tarefa = int(self.tree_tarefa.item(item_selecionado, "text"))
            for tarefa in self.tarefas:
                if tarefa.id == id_tarefa:
                    self.tarefas.remove(tarefa)
                    self.salvar_tarefas_no_banco_de_dados()  
                    self.popular_tarefas()
                    break

    def marcar_concluida(self):
        item_selecionado = self.tree_tarefa.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Por favor, selecione uma tarefa.")
            return

        id_tarefa = int(self.tree_tarefa.item(item_selecionado, "text"))
        for tarefa in self.tarefas:
            if tarefa.id == id_tarefa:
                tarefa.concluida = True
                self.salvar_tarefas_no_banco_de_dados()  
                self.popular_tarefas()
                break
    def verificar_lembretes(self):
        for tarefa in self.tarefas:
            if tarefa.data_limite - datetime.today().date() == timedelta(days=1):
                messagebox.showinfo("Lembrete", f"A tarefa '{tarefa.titulo}' vence amanhã!")
            elif tarefa.data_limite == datetime.today().date():
                messagebox.showinfo("Lembrete", f"A tarefa '{tarefa.titulo}' vence hoje!")

    def carregar_tarefas_do_banco_de_dados(self):
        try:
            with open("tarefas.csv", "r", newline="", encoding="utf-8") as csvfile:
                leitor = csv.DictReader(csvfile)
                for linha in leitor:
                    id = int(linha["ID"])
                    titulo = linha["Título"]
                    descricao = linha["Descrição"]
                    prioridade = linha["Prioridade"]
                    data_limite = datetime.strptime(linha["Data Limite"], "%Y-%m-%d").date()
                    concluida = True if linha["Concluída"].lower() == "true" else False
                    tarefa = Tarefa(id, titulo, descricao, prioridade, data_limite, concluida)
                    self.tarefas.append(tarefa)
        except FileNotFoundError:
            pass

    def salvar_tarefas_no_banco_de_dados(self):
        with open("tarefas.csv", "w", newline="", encoding="utf-8") as csvfile:
            nomes_campos = ["ID", "Título", "Descrição", "Prioridade", "Data Limite", "Concluída"]
            escritor = csv.DictWriter(csvfile, fieldnames=nomes_campos)
            escritor.writeheader()
            for tarefa in self.tarefas:
                escritor.writerow({
                    "ID": tarefa.id,
                    "Título": tarefa.titulo,
                    "Descrição": tarefa.descricao,
                    "Prioridade": tarefa.prioridade,
                    "Data Limite": tarefa.data_limite,
                    "Concluída": tarefa.concluida
                })

    def criar_filtros(self):
        self.frame_filtro = ttk.Frame(self)
        self.frame_filtro.pack(padx=10, pady=5, fill=tk.X)

        self.label_filtro = ttk.Label(self.frame_filtro, text="Filtro:")
        self.label_filtro.grid(row=0, column=0, padx=5, pady=5)

        self.entry_filtro = ttk.Entry(self.frame_filtro)
        self.entry_filtro.grid(row=0, column=1, padx=5, pady=5)

        self.botao_aplicar_filtro = ttk.Button(self.frame_filtro, text="Aplicar", command=self.aplicar_filtro)
        self.botao_aplicar_filtro.grid(row=0, column=2, padx=5, pady=5)

    def aplicar_filtro(self):
        filtro = self.entry_filtro.get().lower()
        tarefas_filtradas = [tarefa for tarefa in self.tarefas if filtro in tarefa.titulo.lower() or filtro in tarefa.descricao.lower() or filtro in tarefa.prioridade.lower()]
        self.popular_tarefas(tarefas_filtradas)

    def criar_ordenacao(self):
        self.frame_ordenacao = ttk.Frame(self)
        self.frame_ordenacao.pack(padx=10, pady=5, fill=tk.X)

        self.label_ordenacao = ttk.Label(self.frame_ordenacao, text="Ordenar por:")
        self.label_ordenacao.grid(row=0, column=0, padx=5, pady=5)

        self.opcoes_ordenacao = ttk.Combobox(self.frame_ordenacao, values=["Data Limite", "Prioridade"])
        self.opcoes_ordenacao.grid(row=0, column=1, padx=5, pady=5)
        self.opcoes_ordenacao.current(0)

        self.botao_aplicar_ordenacao = ttk.Button(self.frame_ordenacao, text="Aplicar", command=self.aplicar_ordenacao)
        self.botao_aplicar_ordenacao.grid(row=0, column=2, padx=5, pady=5)

        self.popular_tarefas()
    def verificar_lembretes(self):
        for tarefa in self.tarefas:
            if tarefa.data_limite - datetime.today().date() == timedelta(days=1):
                messagebox.showinfo("Lembrete", f"A tarefa '{tarefa.titulo}' vence amanhã!")
            elif tarefa.data_limite == datetime.today().date():
                messagebox.showinfo("Lembrete", f"A tarefa '{tarefa.titulo}' vence hoje!")

    def carregar_tarefas_do_banco_de_dados(self):
        try:
            with open("tarefas.csv", "r", newline="", encoding="utf-8") as csvfile:
                leitor = csv.DictReader(csvfile)
                for linha in leitor:
                    id = int(linha["ID"])
                    titulo = linha["Título"]
                    descricao = linha["Descrição"]
                    prioridade = linha["Prioridade"]
                    data_limite = datetime.strptime(linha["Data Limite"], "%Y-%m-%d").date()
                    concluida = True if linha["Concluída"].lower() == "true" else False
                    tarefa = Tarefa(id, titulo, descricao, prioridade, data_limite, concluida)
                    self.tarefas.append(tarefa)
        except FileNotFoundError:
            pass

    def salvar_tarefas_no_banco_de_dados(self):
        with open("tarefas.csv", "w", newline="", encoding="utf-8") as csvfile:
            nomes_campos = ["ID", "Título", "Descrição", "Prioridade", "Data Limite", "Concluída"]
            escritor = csv.DictWriter(csvfile, fieldnames=nomes_campos)
            escritor.writeheader()
            for tarefa in self.tarefas:
                escritor.writerow({
                    "ID": tarefa.id,
                    "Título": tarefa.titulo,
                    "Descrição": tarefa.descricao,
                    "Prioridade": tarefa.prioridade,
                    "Data Limite": tarefa.data_limite,
                    "Concluída": tarefa.concluida
                })

    def criar_filtros(self):
        self.frame_filtro = ttk.Frame(self)
        self.frame_filtro.pack(padx=10, pady=5, fill=tk.X)

        self.label_filtro = ttk.Label(self.frame_filtro, text="Filtro:")
        self.label_filtro.grid(row=0, column=0, padx=5, pady=5)

        self.entry_filtro = ttk.Entry(self.frame_filtro)
        self.entry_filtro.grid(row=0, column=1, padx=5, pady=5)

        self.botao_aplicar_filtro = ttk.Button(self.frame_filtro, text="Aplicar", command=self.aplicar_filtro)
        self.botao_aplicar_filtro.grid(row=0, column=2, padx=5, pady=5)

    def aplicar_filtro(self):
        filtro = self.entry_filtro.get().lower()
        tarefas_filtradas = [tarefa for tarefa in self.tarefas if filtro in tarefa.titulo.lower() or filtro in tarefa.descricao.lower() or filtro in tarefa.prioridade.lower()]
        self.popular_tarefas(tarefas_filtradas)

    def criar_ordenacao(self):
        self.frame_ordenacao = ttk.Frame(self)
        self.frame_ordenacao.pack(padx=10, pady=5, fill=tk.X)

        self.label_ordenacao = ttk.Label(self.frame_ordenacao, text="Ordenar por:")
        self.label_ordenacao.grid(row=0, column=0, padx=5, pady=5)

        self.combo_ordenar = ttk.Combobox(self.frame_ordenacao, values=["Data Limite", "Prioridade"])
        self.combo_ordenar.grid(row=0, column=1, padx=5, pady=5)
        self.combo_ordenar.current(0)

        self.botao_aplicar_ordenacao = ttk.Button(self.frame_ordenacao, text="Aplicar", command=self.ordenar_tarefas)
        self.botao_aplicar_ordenacao.grid(row=0, column=2, padx=5, pady=5)

    def ordenar_tarefas(self):
        ordenar_por = self.combo_ordenar.get()
        if ordenar_por == "Título":
            self.tarefas.sort(key=lambda x: x.titulo)
        elif ordenar_por == "Prioridade":
            self.tarefas.sort(key=lambda x: x.prioridade)
        elif ordenar_por == "Data Limite":
            self.tarefas.sort(key=lambda x: x.data_limite)

        self.popular_tarefas()
    def ao_iniciar_arraste(self, event):
        item_selecionado = self.arvore_tarefas.selection()[0]
        self.item_arrastado = self.arvore_tarefas.identify_row(event.y)
        return True

    def ao_soltar(self, event):
        item_soltado = self.arvore_tarefas.identify_row(event.y)
        tarefa_selecionada = None
        tarefa_arrastada = None


        # Encontrar tarefas selecionadas e arrastadas
        for tarefa in self.tarefas:
            if str(tarefa.id) == self.arvore_tarefas.item(item_soltado, "text"):
                tarefa_selecionada = tarefa
            if str(tarefa.id) == self.arvore_tarefas.item(self.item_arrastado, "text"):
                tarefa_arrastada = tarefa

                # Rearranjar tarefas com base no arraste e solte
            if tarefa_selecionada and tarefa_arrastada:
                indice_selecionado = self.tarefas.index(tarefa_selecionada)
            indice_arrastado = self.tarefas.index(tarefa_arrastada)
            if indice_selecionado < indice_arrastado:
                self.tarefas.insert(indice_selecionado, tarefa_arrastada)
                self.tarefas.pop(indice_arrastado + 1)
            else:
                self.tarefas.insert(indice_selecionado + 1, tarefa_arrastada)
                self.tarefas.pop(indice_arrastado)

        self.popular_tarefas()
        self.salvar_tarefas_no_banco_de_dados()  # Salvar tarefas no banco de dados

    def vincular_arraste_e_solta(self):
        self.arvore_tarefas.bind("<ButtonPress-1>", self.ao_iniciar_arraste)
        self.arvore_tarefas.bind("<B1-Motion>", self.ao_mover_arraste)
        self.arvore_tarefas.bind("<ButtonRelease-1>", self.ao_soltar)

    def ao_mover_arraste(self, event):
        x, y, _, _ = self.arvore_tarefas.bbox(self.item_arrastado)
        self.arvore_tarefas.move(self.item_arrastado, 0, event.y - y)

if __name__ == "__main__":
    app = AplicativoGerenciadorTarefas()
    app.mainloop()