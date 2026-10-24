/** @odoo-module **/

import {registry} from "@web/core/registry";

// "Signing Details" box: placed on the template, but invisible to the person
// signing (no color, no text, not clickable). When the document is signed,
// the server prints the signed date/time and the signer's IP address in it.
const auditSignOca = {
    generate: function (parent, item, signatureItem) {
        signatureItem[0].style.visibility = "hidden";
        signatureItem[0].style.pointerEvents = "none";
        return document.createElement("div");
    },
    check: function () {
        return true;
    },
};
registry.category("sign_oca").add("audit", auditSignOca);
