# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.tools import format_amount, format_date, format_datetime

_logger = logging.getLogger(__name__)

# Field types that do not make sense to expose as a database field to embed
# in a document (too heavy, not meant to be printed, or not a leaf value).
_EXCLUDED_FIELD_TYPES = {"one2many", "binary", "html"}


class SignOcaField(models.Model):
    _name = "sign.oca.field"
    _description = "Signature Field Type"

    name = fields.Char(required=True)
    field_type = fields.Selection(
        [("text", "Text"), ("signature", "Signature"), ("check", "Check")],
        required=True,
        default="text",
    )
    default_value = fields.Char()

    @api.model
    def _get_model_field_choices(self, model_name):
        """Return the list of fields that can be picked as a "database
        field" to pre-fill an item, for the given model.

        Direct fields of ``model_name`` are included, as well as one level
        of relation through many2one fields (e.g. ``partner_id.vat``), so
        that common use cases (partner data, related documents...) do not
        require chaining several dots by hand.

        The list is sorted alphabetically by direct field, but each
        many2one field is immediately followed by its own (alphabetically
        sorted) sub-fields, so e.g. "Company", "Company > City" and
        "Company > State" always stay next to each other, instead of
        "Company > State" ending up scattered away under "S" while
        "Company > City" sits under "C".
        """
        if not model_name or model_name not in self.env:
            return []
        model = self.env[model_name]
        direct_fields = [
            (fname, field)
            for fname, field in model._fields.items()
            if fname != "id" and field.type not in _EXCLUDED_FIELD_TYPES
        ]
        direct_fields.sort(key=lambda item: item[1].string or item[0])

        choices = []
        for fname, field in direct_fields:
            choices.append({"name": fname, "string": field.string or fname})
            if field.type == "many2one" and field.comodel_name in self.env:
                related_model = self.env[field.comodel_name]
                sub_fields = [
                    (sub_fname, sub_field)
                    for sub_fname, sub_field in related_model._fields.items()
                    if sub_fname != "id" and sub_field.type not in _EXCLUDED_FIELD_TYPES
                ]
                sub_fields.sort(key=lambda item: item[1].string or item[0])
                for sub_fname, sub_field in sub_fields:
                    choices.append(
                        {
                            "name": f"{fname}.{sub_fname}",
                            "string": f"{field.string} > {sub_field.string}",
                        }
                    )
        return choices

    @api.model
    def _get_field_display_value(self, record, field_path):
        """Resolve a (possibly dotted) field path on ``record`` and return
        a human readable string suitable to be printed on a document.

        Returns an empty string whenever the record, the path, or any
        intermediate value is missing, instead of raising, so that a wrong
        or outdated configuration never blocks the signature flow.
        """
        if not record or not field_path:
            return ""
        try:
            current = record
            chain = field_path.split(".")
            for fname in chain[:-1]:
                if fname not in current._fields:
                    return ""
                current = current[fname]
                if not current:
                    return ""
            fname = chain[-1]
            if fname not in current._fields:
                return ""
            field = current._fields[fname]
            value = current[fname]
            return self._format_field_display_value(current, field, value)
        except Exception:
            _logger.exception(
                "Error getting the value of field '%s' for a sign.oca item",
                field_path,
            )
            return ""

    @api.model
    def _format_field_display_value(self, record, field, value):
        if not value:
            return ""
        if field.type == "many2one":
            return value.display_name
        if field.type in ("many2many", "one2many"):
            return ", ".join(value.mapped("display_name"))
        if field.type == "date":
            return format_date(self.env, value)
        if field.type == "datetime":
            return format_datetime(self.env, value)
        if field.type == "monetary":
            currency = (
                field.currency_field
                and record[field.currency_field]
                or self.env.company.currency_id
            )
            return format_amount(self.env, value, currency)
        if field.type == "selection":
            try:
                selection = field._description_selection(self.env)
            except Exception:
                selection = field.selection if isinstance(field.selection, list) else []
            return str(dict(selection).get(value, value))
        return str(value)
