from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        product = self.env.ref("product.product_product_4")
        picking_type = self.env.ref("stock.picking_type_out")
        # Create a picking in 'assigned' state with exceptions
        self.picking_with_exceptions = self.env["stock.picking"].create(
            {
                "name": "Test Picking With Exceptions 2",
                "state": "assigned",
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Move With Exceptions",
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "reserved_availability": 1,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    )
                ],
                "ignore_exception": False,
            }
        )

    def test_detect_exceptions(self):
        # Test that exceptions are detected for the picking with exceptions
        exceptions = self.picking_with_exceptions.detect_exceptions()
        self.assertTrue(exceptions, "Exceptions should be detected")

    def test_button_validate(self):
        initial_state = self.picking_with_exceptions.state
        result = self.picking_with_exceptions.button_validate()

        self.assertEqual(
            self.picking_with_exceptions.state,
            initial_state,
            "Picking state should remain the same due to exceptions",
        )

        # Verify the result of the validated action
        if (
            self.picking_with_exceptions.detect_exceptions()
            and not self.picking_with_exceptions.ignore_exception
        ):
            self.assertIsNotNone(
                result, "Action validate should return a result if not proceeding"
            )
        else:
            self.assertIsNone(
                result, "Action validate should not return a result if proceeding"
            )

    def test_onchange_ignore_exception(self):
        # Change state and verify onchange behavior for picking
        self.picking_with_exceptions.write(
            {"state": "waiting", "ignore_exception": True}
        )
        self.assertTrue(self.picking_with_exceptions.ignore_exception)
