from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _create_backorder(self):
        res = super(StockPicking, self)._create_backorder()
        for original_move in self.move_ids:
            corresponding_move = next(
                (
                    move
                    for move in res.move_ids
                    if move.product_id == original_move.product_id
                ),
                None,
            )
            if corresponding_move and corresponding_move.secondary_uom_qty:
                # To avoid rounding errors, Saving the current value of product_uom_qty
                # before recalculating the secondary unit. Afterward,
                # I'll restore the original value
                product_uom_qty = corresponding_move.product_uom_qty
                corresponding_move.with_context(
                    bypass_compute_field_qty=True
                )._compute_secondary_uom_qty()
                corresponding_move.product_uom_qty = product_uom_qty
            else:
                continue
        return res
