import platform

from .vendor.Qt import QtWidgets, QtGui, QtCore

from . import model
from .awesome import tags as awesome
from .constants import (
    PluginStates, InstanceStates, PluginActionStates, GroupStates, Roles
)

colors = {
    "error": QtGui.QColor("#ff4a4a"),
    "warning": QtGui.QColor("#ff9900"),
    "ok": QtGui.QColor("#77AE24"),
    "active": QtGui.QColor("#99CEEE"),
    "idle": QtCore.Qt.white,
    "font": QtGui.QColor("#DDD"),
    "inactive": QtGui.QColor("#888"),
    "hover": QtGui.QColor(255, 255, 255, 10),
    "selected": QtGui.QColor(255, 255, 255, 20),
    "outline": QtGui.QColor("#333"),
    "group": QtGui.QColor("#333")
}

group_fg_colors = {
    "error": QtGui.QColor("#aa5050"),
    "warning": QtGui.QColor("#b36b00"),
    "ok": QtGui.QColor("#458056"),
    "group": QtGui.QColor("#ffffff")
}

scale_factors = {"darwin": 1.5}
scale_factor = scale_factors.get(platform.system().lower(), 1.0)
fonts = {
    "h3": QtGui.QFont("Open Sans", 10 * scale_factor, 900),
    "h4": QtGui.QFont("Open Sans", 8 * scale_factor, 400),
    "h5": QtGui.QFont("Open Sans", 8 * scale_factor, 800),
    "awesome6": QtGui.QFont("FontAwesome", 6 * scale_factor),
    "awesome10": QtGui.QFont("FontAwesome", 10 * scale_factor),
    "smallAwesome": QtGui.QFont("FontAwesome", 8 * scale_factor),
    "largeAwesome": QtGui.QFont("FontAwesome", 16 * scale_factor),
}
font_metrics = {
    "awesome6": QtGui.QFontMetrics(fonts["awesome6"]),
    "h4": QtGui.QFontMetrics(fonts["h4"]),
    "h5": QtGui.QFontMetrics(fonts["h5"])
}
icons = {
    "action": awesome["adn"],
    "angle-right": awesome["angle-right"],
    "angle-left": awesome["angle-left"],
    "plus-sign": awesome['plus'],
    "minus-sign": awesome['minus']
}


class PluginItemDelegate(QtWidgets.QStyledItemDelegate):
    """Generic delegate for model items"""

    def paint(self, painter, option, index):
        """Paint checkbox and text.
         _
        |_|  My label    >
        """

        body_rect = QtCore.QRectF(option.rect)

        check_rect = QtCore.QRectF(body_rect)
        check_rect.setWidth(check_rect.height())
        check_offset = (check_rect.height() / 4) + 1
        check_rect.adjust(
            check_offset, check_offset, -check_offset, -check_offset
        )

        check_color = colors["idle"]

        perspective_icon = icons["angle-right"]
        perspective_rect = QtCore.QRectF(body_rect)
        perspective_rect.setWidth(perspective_rect.height())
        perspective_rect.adjust(0, 3, 0, 0)
        perspective_rect.translate(
            body_rect.width() - (perspective_rect.width() / 2 + 2),
            0
        )

        publish_states = index.data(Roles.PublishFlagsRole)
        if publish_states & PluginStates.InProgress:
            check_color = colors["active"]

        elif publish_states & PluginStates.HasError:
            check_color = colors["error"]

        elif publish_states & PluginStates.HasWarning:
            check_color = colors["warning"]

        elif publish_states & PluginStates.WasProcessed:
            check_color = colors["ok"]

        elif not index.data(Roles.IsEnabledRole):
            check_color = colors["inactive"]

        offset = (body_rect.height() - font_metrics["h4"].height()) / 2
        label_rect = QtCore.QRectF(body_rect.adjusted(
            check_rect.width() + 12, offset - 1, 0, 0
        ))

        assert label_rect.width() > 0

        label = index.data(QtCore.Qt.DisplayRole)
        label = font_metrics["h4"].elidedText(
            label,
            QtCore.Qt.ElideRight,
            label_rect.width() - 20
        )

        font_color = colors["idle"]
        if not index.data(QtCore.Qt.CheckStateRole):
            font_color = colors["inactive"]

        # Maintain reference to state, so we can restore it once we're done
        painter.save()

        # Draw perspective icon
        painter.setFont(fonts["awesome10"])
        painter.setPen(QtGui.QPen(font_color))
        painter.drawText(perspective_rect, perspective_icon)

        # Draw label
        painter.setFont(fonts["h4"])
        painter.setPen(QtGui.QPen(font_color))
        painter.drawText(label_rect, label)

        # Draw action icon
        if index.data(Roles.PluginActionsVisibleRole):
            painter.save()
            action_state = index.data(Roles.PluginActionProgressRole)
            if action_state & PluginActionStates.HasFailed:
                color = colors["error"]
            elif action_state & PluginActionStates.HasFinished:
                color = colors["ok"]
            elif action_state & PluginActionStates.InProgress:
                color = colors["active"]
            else:
                color = colors["idle"]

            painter.setFont(fonts["smallAwesome"])
            painter.setPen(QtGui.QPen(color))

            icon_rect = QtCore.QRectF(
                option.rect.adjusted(
                    label_rect.width() - perspective_rect.width()/2,
                    label_rect.height() / 3, 0, 0
                )
            )
            painter.drawText(icon_rect, icons["action"])

            painter.restore()

        # Draw checkbox
        pen = QtGui.QPen(check_color, 1)
        painter.setPen(pen)

        if index.data(Roles.IsOptionalRole):
            painter.drawRect(check_rect)

            if index.data(QtCore.Qt.CheckStateRole):
                optional_check_rect = QtCore.QRectF(check_rect)
                optional_check_rect.adjust(2, 2, -1, -1)
                painter.fillRect(optional_check_rect, check_color)

        else:
            painter.fillRect(check_rect, check_color)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(body_rect, colors["hover"])

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(body_rect, colors["selected"])

        # Ok, we're done, tidy up.
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width(), 20)


class InstanceItemDelegate(QtWidgets.QStyledItemDelegate):
    """Generic delegate for model items"""

    def paint(self, painter, option, index):
        """Paint checkbox and text.
         _
        |_|  My label    >
        """

        body_rect = QtCore.QRectF(option.rect)

        check_rect = QtCore.QRectF(body_rect)
        check_rect.setWidth(check_rect.height())
        offset = (check_rect.height() / 4) + 1
        check_rect.adjust(offset, offset, -(offset), -(offset))

        check_color = colors["idle"]

        perspective_icon = icons["angle-right"]
        perspective_rect = QtCore.QRectF(body_rect)
        perspective_rect.setWidth(perspective_rect.height())
        perspective_rect.adjust(0, 3, 0, 0)
        perspective_rect.translate(
            body_rect.width() - (perspective_rect.width() / 2 + 2),
            0
        )

        publish_states = index.data(Roles.PublishFlagsRole)
        if publish_states & InstanceStates.InProgress:
            check_color = colors["active"]

        elif publish_states & InstanceStates.HasError:
            check_color = colors["error"]

        elif publish_states & InstanceStates.HasWarning:
            check_color = colors["warning"]

        elif publish_states & InstanceStates.HasFinished:
            check_color = colors["ok"]

        elif not index.data(Roles.IsEnabledRole):
            check_color = colors["inactive"]

        offset = (body_rect.height() - font_metrics["h4"].height()) / 2
        label_rect = QtCore.QRectF(body_rect.adjusted(
            check_rect.width() + 12, offset - 1, 0, 0
        ))

        assert label_rect.width() > 0

        label = index.data(QtCore.Qt.DisplayRole)
        label = font_metrics["h4"].elidedText(
            label,
            QtCore.Qt.ElideRight,
            label_rect.width() - 20
        )

        font_color = colors["idle"]
        if not index.data(QtCore.Qt.CheckStateRole):
            font_color = colors["inactive"]

        # Maintain reference to state, so we can restore it once we're done
        painter.save()

        # Draw perspective icon
        painter.setFont(fonts["awesome10"])
        painter.setPen(QtGui.QPen(font_color))
        painter.drawText(perspective_rect, perspective_icon)

        # Draw label
        painter.setFont(fonts["h4"])
        painter.setPen(QtGui.QPen(font_color))
        painter.drawText(label_rect, label)

        # Draw checkbox
        pen = QtGui.QPen(check_color, 1)
        painter.setPen(pen)

        if index.data(Roles.IsOptionalRole):
            painter.drawRect(check_rect)

            if index.data(QtCore.Qt.CheckStateRole):
                optional_check_rect = QtCore.QRectF(check_rect)
                optional_check_rect.adjust(2, 2, -1, -1)
                painter.fillRect(optional_check_rect, check_color)

        else:
            painter.fillRect(check_rect, check_color)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(body_rect, colors["hover"])

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(body_rect, colors["selected"])

        # Ok, we're done, tidy up.
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width(), 20)


class OverviewGroupSection(QtWidgets.QStyledItemDelegate):
    """Generic delegate for section header"""

    item_class = None

    def __init__(self, parent):
        super(OverviewGroupSection, self).__init__(parent)
        self.item_delegate = self.item_class(parent)

    def paint(self, painter, option, index):
        if index.data(Roles.TypeRole) in (
            model.InstanceType, model.PluginType
        ):
            self.item_delegate.paint(painter, option, index)
            return

        self.group_item_paint(painter, option, index)

    def pick_fg_colors(self, index):
        key = "group"
        publish_states = index.data(Roles.PublishFlagsRole)
        if publish_states & GroupStates.HasWarning:
            key = "warning"
        elif publish_states & GroupStates.HasError:
            key = "error"
        elif publish_states & GroupStates.HasFinished:
            key = "ok"
        return group_fg_colors[key]

    def group_item_paint(self, painter, option, index):
        """Paint text
         _
        My label
        """
        body_rect = QtCore.QRectF(option.rect)
        bg_rect = QtCore.QRectF(
            body_rect.left(), body_rect.top() + 1,
            body_rect.width() - 5, body_rect.height() - 2
        )
        fg_color = self.pick_fg_colors(index)
        radius = 8.0
        bg_path = QtGui.QPainterPath()
        bg_path.addRoundedRect(bg_rect, radius, radius)
        painter.fillPath(bg_path, colors["group"])

        expander_rect = QtCore.QRectF(bg_rect)
        expander_rect.setWidth(expander_rect.height())
        text_height = font_metrics["awesome6"].height()
        adjust_value = (expander_rect.height() - text_height) / 2
        expander_rect.adjust(
            adjust_value + 1.5, adjust_value - 0.5,
            -adjust_value + 1.5, -adjust_value - 0.5
        )

        offset = (bg_rect.height() - font_metrics["h5"].height()) / 2
        label_rect = QtCore.QRectF(bg_rect.adjusted(
            expander_rect.width() + 12, offset - 1, 0, 0
        ))

        assert label_rect.width() > 0

        expander_icon = icons["plus-sign"]

        expanded = self.parent().isExpanded(index)
        if expanded:
            expander_icon = icons["minus-sign"]
        label = index.data(QtCore.Qt.DisplayRole)
        label = font_metrics["h5"].elidedText(
            label, QtCore.Qt.ElideRight, label_rect.width()
        )

        # Maintain reference to state, so we can restore it once we're done
        painter.save()

        painter.setFont(fonts["awesome6"])
        painter.setPen(QtGui.QPen(fg_color))
        painter.drawText(expander_rect, expander_icon)

        # Draw label
        painter.setFont(fonts["h5"])
        painter.drawText(label_rect, label)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillPath(bg_path, colors["hover"])

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillPath(bg_path, colors["selected"])

        # Ok, we're done, tidy up.
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width(), 20)


class PluginDelegate(OverviewGroupSection):
    """Generic delegate for model items in proxy tree view"""
    item_class = PluginItemDelegate


class InstanceDelegate(OverviewGroupSection):
    """Generic delegate for model items in proxy tree view"""
    item_class = InstanceItemDelegate


class ArtistDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate used on Artist page"""

    def paint(self, painter, option, index):
        """Paint checkbox and text

         _______________________________________________
        |       |  label              | duration  |arrow|
        |toggle |_____________________|           | to  |
        |       |  families           |           |persp|
        |_______|_____________________|___________|_____|

        """

        # Layout
        spacing = 10
        metrics = painter.fontMetrics()

        body_rect = QtCore.QRectF(option.rect).adjusted(2, 2, -8, -2)
        content_rect = body_rect.adjusted(5, 5, -5, -5)

        toggle_rect = QtCore.QRectF(body_rect)
        toggle_rect.setWidth(7)
        toggle_rect.adjust(1, 1, 0, -1)

        icon_rect = QtCore.QRectF(content_rect)
        icon_rect.translate(toggle_rect.width() + spacing, 3)
        icon_rect.setWidth(35)
        icon_rect.setHeight(35)

        duration_rect = QtCore.QRectF(content_rect)
        duration_rect.translate(content_rect.width() - 50, 0)

        label_rect = QtCore.QRectF(content_rect)
        label_rect.translate(
            icon_rect.width() + spacing,
            0
        )
        label_rect.setHeight(metrics.lineSpacing() + spacing)

        families_rect = QtCore.QRectF(label_rect)
        families_rect.translate(0, label_rect.height())

        perspective_rect = QtCore.QRectF(body_rect)
        perspective_rect.setWidth(35)
        perspective_rect.setHeight(35)
        perspective_rect.translate(
            content_rect.width() - (perspective_rect.width() / 2) + 10,
            (content_rect.height() / 2) - (perspective_rect.height() / 2)
        )

        # Colors
        check_color = colors["idle"]

        publish_states = index.data(Roles.PublishFlagsRole)
        if publish_states is None:
            return
        if publish_states & InstanceStates.InProgress:
            check_color = colors["active"]

        elif publish_states & InstanceStates.HasError:
            check_color = colors["error"]

        elif publish_states & InstanceStates.HasWarning:
            check_color = colors["warning"]

        elif publish_states & InstanceStates.HasFinished:
            check_color = colors["ok"]

        elif not index.data(Roles.IsEnabledRole):
            check_color = colors["inactive"]

        icon = index.data(QtCore.Qt.DecorationRole)
        perspective_icon = icons["angle-right"]
        label = index.data(QtCore.Qt.DisplayRole)

        families = ", ".join(index.data(Roles.FamiliesRole))

        # Elide
        label = metrics.elidedText(
            label, QtCore.Qt.ElideRight, label_rect.width()
        )

        families = metrics.elidedText(
            families, QtCore.Qt.ElideRight, label_rect.width()
        )

        font_color = colors["idle"]
        if not index.data(QtCore.Qt.CheckStateRole):
            font_color = colors["inactive"]

        perspective_color = colors["inactive"]
        if (
            option.state
            & (
                QtWidgets.QStyle.State_MouseOver
                or QtWidgets.QStyle.State_Selected
            )
        ):
            perspective_color = colors["idle"]
        # Maintan reference to state, so we can restore it once we're done
        painter.save()

        # Draw background
        painter.fillRect(body_rect, colors["hover"])

        painter.setFont(fonts["largeAwesome"])
        painter.setPen(QtGui.QPen(font_color))
        painter.drawText(icon_rect, icon)

        # Draw label
        painter.setFont(fonts["h3"])
        painter.drawText(label_rect, label)

        # Draw families
        painter.setFont(fonts["h5"])
        painter.setPen(QtGui.QPen(colors["inactive"]))
        painter.drawText(families_rect, families)

        painter.setFont(fonts["largeAwesome"])
        painter.setPen(QtGui.QPen(perspective_color))
        painter.drawText(perspective_rect, perspective_icon)

        # Draw checkbox
        pen = QtGui.QPen(check_color, 1)
        painter.setPen(pen)

        if index.data(Roles.IsOptionalRole):
            painter.drawRect(toggle_rect)

            if index.data(QtCore.Qt.CheckStateRole):
                painter.fillRect(toggle_rect, check_color)

        elif (
            index.data(QtCore.Qt.CheckStateRole)
        ):
            painter.fillRect(toggle_rect, check_color)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(body_rect, colors["hover"])

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(body_rect, colors["selected"])

        painter.setPen(colors["outline"])
        painter.drawRect(body_rect)

        # Ok, we're done, tidy up.
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width(), 80)


class TerminalItem(QtWidgets.QStyledItemDelegate):
    """Delegate used exclusively for the Terminal"""

    def paint(self, painter, option, index):
        super(TerminalItem, self).paint(painter, option, index)
        item_type = index.data(Roles.TypeRole)
        if item_type == model.TerminalDetailType:
            return

        hover = QtGui.QPainterPath()
        hover.addRect(QtCore.QRectF(option.rect).adjusted(0, 0, -1, -1))
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillPath(hover, colors["selected"])

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillPath(hover, colors["hover"])
