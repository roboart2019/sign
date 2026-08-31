/** @odoo-module **/
/* global Event */

import {registry} from "@web/core/registry";
import {renderToString} from "@web/core/utils/render";

const textSignOca = {
    change: function (value, parent, item) {
        item.value = value;
        parent.checkFilledAll();
    },
    generate: function (parent, item, signatureItem) {
        var input = $(
            renderToString("sign_oca.sign_iframe_field_text", {
                item: item,
                role_id: parent.info.role_id,
            })
        )[0];
        // The field starts readonly so the browser does not consider it
        // fillable on page load (Chrome, in particular, ignores
        // autocomplete="off" for fields it heuristically detects as
        // address-related, which these are: they sit right next to real
        // "City:"/"State:" text in the PDF). It is unlocked as soon as the
        // field is actually focused, so typing/editing behaves normally.
        const unlock = () => {
            input.removeAttribute("readonly");
        };
        // Only a real gesture on THIS field counts as the signer engaging
        // with it. Programmatic focus (e.g. the navigator jumping to the
        // next field) deliberately does not, so that a browser autofill
        // pass can never be mistaken for the signer editing the value.
        let userEngaged = false;
        const engage = () => {
            userEngaged = true;
            unlock();
        };
        input.addEventListener("mousedown", engage);
        input.addEventListener("touchstart", engage);
        signatureItem[0].addEventListener("focus_signature", () => {
            unlock();
            input.focus();
        });
        input.addEventListener("focus", (ev) => {
            unlock();
            if (
                item.default_value &&
                !item.value &&
                parent.info.partner[item.default_value]
            ) {
                this.change(
                    parent.info.partner[item.default_value],
                    parent,
                    item,
                    signatureItem
                );
                ev.target.value = parent.info.partner[item.default_value];
            }
        });
        input.addEventListener("change", (ev) => {
            if (!userEngaged) {
                // Nobody touched this field, so this "change" did not come
                // from the signer: it is the browser autofilling over a
                // value we put there (typically a pre-filled database
                // value). Keep the real value and put it back on screen
                // instead of writing the browser's guess into the record.
                ev.srcElement.value = item.value || "";
                return;
            }
            this.change(ev.srcElement.value, parent, item, signatureItem);
        });
        input.addEventListener("keydown", (ev) => {
            if ((ev.keyCode || ev.which) !== 9) {
                // Any other key means the signer is typing in this field.
                engage();
                return true;
            }
            ev.preventDefault();
            var next_items = Object.values(parent.info.items)
                .filter(
                    (i) =>
                        i.tabindex > item.tabindex && i.role_id === parent.info.role_id
                )
                .sort((a, b) => a.tabindex - b.tabindex);
            if (next_items.length > 0) {
                ev.currentTarget.blur();
                const nextItem = next_items[0];
                if (nextItem && parent.items && parent.items[nextItem.id]) {
                    parent.items[nextItem.id].dispatchEvent(
                        new Event("focus_signature")
                    );
                }
            }
        });
        return input;
    },
    check: function (item) {
        return Boolean(item.value);
    },
};
registry.category("sign_oca").add("text", textSignOca);
export default textSignOca;
