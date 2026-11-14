import sqlite3
from datetime import datetime
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

    # Texto de resumo do total acumulado
    texto_total = ft.Text(
        "Total acumulado: R$ 0,00",
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

    # 3. Função para ler o banco e reconstruir a lista na tela
    def carregar_gastos():
        lista_gastos.controls.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, data, item, valor FROM gastos ORDER BY id DESC")
        registos = cursor.fetchall()
        conn.close()

        soma_total = 0.0
        for id_gasto, data, item, valor in registos:
            soma_total += valor
            lista_gastos.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=ft.Colors.TEAL_700),
                        title=ft.Text(item, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(data, size=12),
                        trailing=ft.Text(
                            f"R$ {valor:.2f}".replace(".", ","),
                            color=ft.Colors.TEAL_800,
                            weight=ft.FontWeight.BOLD,
                            size=14,
                        ),
                    )
                )
            )
        texto_total.value = f"Total acumulado: R$ {soma_total:.2f}".replace(".", ",")
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
