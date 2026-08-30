/** @odoo-module */
/* Copyright 2024 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {Dialog} from "@web/core/dialog/dialog";
import {useChildRef} from "@web/core/utils/hooks";

import {Component} from "@odoo/owl";

export class SignOcaConfigureFieldDialog extends Component {
    setup() {
        this.env.dialogData.dismiss = () => this._cancel();
        this.modalRef = useChildRef();
        this.isProcess = false;
    }

    async _cancel() {
        this.props.close();
    }

    _onFieldNameChange(ev) {
        const $el = $(this.modalRef.el);
        const hasFieldName = Boolean(ev.target.value);
        $el.find('select[name="role_id"]').prop("disabled", hasFieldName);
        $el.find("input[name='required']").prop("disabled", hasFieldName);
    }

    async _confirm() {
        const $el = $(this.modalRef.el);
        const fieldName = $el.find('select[name="field_name"]').val() || false;
        await this.props.confirm(
            parseInt($el.find('select[name="field_id"]').val(), 10),
            fieldName ? false : parseInt($el.find('select[name="role_id"]').val(), 10),
            fieldName ? false : $el.find("input[name='required']").prop("checked"),
            $el.find("input[name='placeholder']").val(),
            fieldName
        );
        this.props.close();
    }

    async _delete() {
        this.props.delete();
        this.props.close();
    }
}
SignOcaConfigureFieldDialog.template = "sign_oca.SignOcaConfigureFieldDialog";
SignOcaConfigureFieldDialog.components = {Dialog};
SignOcaConfigureFieldDialog.props = {
    close: Function,
    title: {
        validate: (m) => {
            return (
                typeof m === "string" ||
                (typeof m === "object" && typeof m.toString === "function")
            );
        },
    },
    item: Object,
    info: Object,
    confirm: Function,
    delete: Function,
};
