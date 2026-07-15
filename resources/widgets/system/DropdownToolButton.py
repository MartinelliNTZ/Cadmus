# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QToolButton, QMenu


class DropdownToolButton(QToolButton):
    """
    Widget para botão dropdown na toolbar do QGIS.

    Herda de QToolButton para ser adicionado como widget à toolbar.
    """

    # Compatibilidade Qt5/Qt6: Qt5 usa QToolButton.MenuButtonPopup,
    # Qt6 usa QToolButton.ToolButtonPopupMode.MenuButtonPopup
    @staticmethod
    def _popup_mode():
        try:
            return QToolButton.ToolButtonPopupMode.MenuButtonPopup
        except AttributeError:
            return QToolButton.MenuButtonPopup

    def __init__(
        self,
        iface=None,
        title=None,
        main_action=None,
        secondary_actions=None,
        icon=None,
    ):
        """
        Inicializa o botão dropdown.

        :param iface: Interface do QGIS (usado para mainWindow() do menu)
        :param title: Texto do botão
        :param main_action: QAction principal (ação padrão ao clicar)
        :param secondary_actions: Lista de QActions adicionais no menu
        :param icon: QIcon opcional (usa ícone da main_action se None)
        """
        super().__init__()
        self.menu = QMenu(iface.mainWindow() if iface else None)
        self.setPopupMode(self._popup_mode())
        self.setMenu(self.menu)

        if main_action is not None:
            self.setup(title, main_action, secondary_actions, icon)

    def setup(self, title, main_action, secondary_actions=None, icon=None):
        """
        Configura o botão dropdown com ações.

        :param title: Texto do botão
        :param main_action: QAction principal (ação padrão ao clicar)
        :param secondary_actions: Lista de QActions adicionais no menu
        :param icon: QIcon opcional (usa ícone da main_action se None)
        """
        if secondary_actions is None:
            secondary_actions = []

        self.setText(title)
        self.setIcon(icon or main_action.icon())
        self.setToolTip(main_action.toolTip())

        # Conectar o clique principal à ação principal
        self.clicked.connect(main_action.trigger)

        self.menu.clear()
        self.menu.setToolTipsVisible(True)
        self.menu.addAction(main_action)  # Ação principal no topo

        for act in secondary_actions:
            if act is None:
                self.menu.addSeparator()
            else:
                self.menu.addAction(act)
