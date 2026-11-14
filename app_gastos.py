import sqlite3
from datetime import datetime
from collections import defaultdict
import flet as ft

#def base dados
DB_NAME = "gastos_app.db"

def inicializar_bd():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            item TEXT NOT NULL,
            valor REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def main(page: ft.Page):
    # Configurações gerais da janela/tela
    page.title = "Gestor de Gastos"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    inicializar_bd()

    # 1. Campos de entrada de dados
    input_item = ft.TextField(
        label="Descrição do gasto (ex: Supermercado)",
        width=340,
        border_radius=8,
    )
    input_valor = ft.TextField(
        label="Valor (ex: 45,90)",
        width=340,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
    )

    # Texto de resumo do total geral acumulado
    texto_total = ft.Text(
        "Total geral acumulado: R$ 0,00",
        size=14,
        weight=ft.FontWeight.BOLD,
    )
    # 2. Lista visual rolável
    lista_gastos = ft.ListView(expand=True, spacing=8, padding=5)

    def mostrar_aviso(mensagem, cor):
        snack = ft.SnackBar(
            content=ft.Text(mensagem, color=ft.Colors.WHITE),
            bgcolor=cor,
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    # Nova função para deletar um gasto pelo ID
    def deletar_gasto(id_gasto):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            # O comando DELETE usa o ID único para apagar apenas o item escolhido
            cursor.execute("DELETE FROM gastos WHERE id = ?", (id_gasto,))
            conn.commit()
            conn.close()
            
            # Atualiza a lista na tela e o total acumulado
            carregar_gastos()
            mostrar_aviso("Gasto excluído com sucesso!", ft.Colors.ORANGE_700)
        except Exception as erro:
            mostrar_aviso(f"Erro ao excluir: {erro}", ft.Colors.RED_600)

   
    #3 Função para ler o banco, agrupar por dia e montar a interface
    def carregar_gastos():
        lista_gastos.controls.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, data, item, valor FROM gastos ORDER BY id DESC")
        registos = cursor.fetchall()
        conn.close()

        soma_geral = 0.0
        
        # Dicionário para agrupar os gastos por dia (extraindo apenas a data DD/MM/AAAA)
        dias_dict = defaultdict(list)
        
        for id_gasto, data_hora, item, valor in registos:
            soma_geral += valor
            dia_apenas = data_hora.split(" ")[0]
            hora_apenas = data_hora.split(" ")[1] if " " in data_hora else ""
            dias_dict[dia_apenas].append((id_gasto, hora_apenas, item, valor))

        # Para cada dia encontrado, criamos um bloco/cartão calendário
        for dia, itens_do_dia in dias_dict.items():
            soma_dia = sum(v for _, _, _, v in itens_do_dia)
            
            controles_do_dia = []
            for id_gasto, hora, item, valor in itens_do_dia:
                btn_excluir = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Excluir gasto",
                    on_click=lambda e, id_atual=id_gasto: deletar_gasto(id_atual),
                )
                
                controles_do_dia.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=ft.Colors.TEAL_700, size=20),
                        title=ft.Text(item, weight=ft.FontWeight.BOLD, size=13),
                        subtitle=ft.Text(f"Horário: {hora}", size=11),
                        trailing=ft.Row(
                            [
                                ft.Text(
                                    f"R$ {valor:.2f}".replace(".", ","),
                                    color=ft.Colors.TEAL_800,
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                ),
                                btn_excluir,
                            ],
                            tight=True,
                        ),
                    )
                )

            lista_gastos.controls.append(
                ft.Card(
                    content=ft.ExpansionTile(
                        title=ft.Text(f"📅 Dia {dia}", weight=ft.FontWeight.BOLD, size=14),
                        subtitle=ft.Text(f"Total do dia: R$ {soma_dia:.2f}".replace(".", ","), size=12, color=ft.Colors.TEAL_900),
                        initially_expanded=True,
                        controls=controles_do_dia,
                        tile_padding=10,
                    )
                )
            )

        texto_total.value = f"Total geral acumulado: R$ {soma_geral:.2f}".replace(".", ",")
        page.update()

    # 4. Evento de clique do botão Adicionar
    def adicionar_gasto(e):
        if not input_item.value or not input_valor.value:
            mostrar_aviso("Preencha a descrição e o valor!", ft.Colors.RED_600)
            return

        try:
            item = input_item.value.strip()
            valor_limpo = input_valor.value.strip().replace(",", ".")
            valor = float(valor_limpo)

            if valor <= 0:
                mostrar_aviso("O valor deve ser maior que zero.", ft.Colors.RED_600)
                return

            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (data, item, valor) VALUES (?, ?, ?)",
                (data_atual, item, valor),
            )
            conn.commit()
            conn.close()

            # Limpa os campos e recarrega a interface
            input_item.value = ""
            input_valor.value = ""
            carregar_gastos()
            mostrar_aviso("Gasto registrado com sucesso!", ft.Colors.GREEN_700)

        except ValueError:
            mostrar_aviso("Valor inválido. Digite apenas números.", ft.Colors.RED_600)

    # Botão adaptado para o Flet 1.1.2
    btn_adicionar = ft.Button(
        content="Registrar Gasto",
        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
        on_click=adicionar_gasto,
        width=340,
        height=45,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.TEAL_700,
        ),
    )

    # 5. Montagem final dos elementos na tela
    page.add(
        ft.Text("Controle de Gastos", size=22, weight=ft.FontWeight.BOLD),
        input_item,
        input_valor,
        btn_adicionar,
        ft.Divider(),
        texto_total,
        ft.Container(content=lista_gastos, expand=True, width=360),
    )

    carregar_gastos()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)
