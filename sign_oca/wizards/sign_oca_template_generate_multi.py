# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SignOcaTemplateGenerateMulti(models.TransientModel):
    _name = "sign.oca.template.generate.multi"
    _description = "Generate signature requests"

    model = fields.Char(
        readonly=True,
        default=lambda self: self.env.context.get("active_model")
        or self.env.context.get("model", False),
    )
    # Snapshot the records the wizard was opened for right away, instead of
    # reading "active_ids"/"active_id" from context again when "Generate"
    # is pressed: that context is not guaranteed to still be sent along
    # with a later button call, which otherwise silently produces zero
    # records.
    res_ids = fields.Char(
        readonly=True,
        default=lambda self: ",".join(
            str(res_id) for res_id in self._get_default_res_ids()
        ),
    )
    template_id = fields.Many2one(
        comodel_name="sign.oca.template",
        # Templates not linked to any model can be used for any record,
        # in addition to templates linked to this specific model.
        domain="['|', ('model', '=', False), ('model', '=', model)]",
        required=True,
    )
    message = fields.Html()

    def _get_default_res_ids(self):
        # A form view only sets "active_id" (no "active_ids"); support both
        # so this wizard works from a list view (multiple records) and from
        # a single record's own form view.
        return self.env.context.get("active_ids") or (
            self.env.context.get("active_id") and [self.env.context["active_id"]]
        ) or []

    def _get_res_ids(self):
        self.ensure_one()
        return [int(res_id) for res_id in (self.res_ids or "").split(",") if res_id]

    def _prepare_sign_oca_request_vals(self):
        vals = []
        for item in self.env[self.model].browse(self._get_res_ids()):
            vals.append(
                self.template_id._prepare_sign_oca_request_vals_from_record(item)
            )
        return vals

    def _generate(self):
        return self.env["sign.oca.request"].create(
            self._prepare_sign_oca_request_vals()
        )

    def generate(self):
        requests = self._generate()
        for request in requests:
            request.action_send(message=self.message)
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sign_oca.sign_oca_request_act_window"
        )
        action["domain"] = [("id", "in", requests.ids)]
        return action
