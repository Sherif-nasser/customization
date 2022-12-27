frappe.provide("erpnext.accounts.dimensions");
frappe.ui.form.on('Payment Entry', {
    refresh	: function(frm) {
		let references = frm.doc.references;
		let Doctype = false;
		// console.log(references[0].reference_doctype);
		if (references.length >= 0) {
			for(var i = 0; i <= references.length -1 ; i++){
				if(references[i].reference_doctype == 'Fees'){
					Doctype = true;
					console.log(references[i].reference_doctype)
					console.log(Doctype)
				}
			}
			}
		else{
			Doctype = false;
			console.log(Doctype);
		}
		if (!frm.is_new() && frm.doc.docstatus === 1 && Doctype == true){
			
			var button = frm.add_custom_button(('Create cost allocation'), function(buttonDimmed){
				
				let DocName = $("#navbar-breadcrumbs")[0].children[2].innerText;
				console.log(DocName);
				
					return frappe.call({
						method: "erpnext.controllers.Custom_queries.create_JornalEntry_from_PaymentEntry",
						args: {
							docname : DocName,
						}
						});

			}).click(function(){
				// let butdisabled = $(".page-head-content")[0].children[1].children[1].children[1];
				frm.remove_custom_button('Create cost allocation');
				frappe.show_alert({
					message:__('Jornal Entry created succesfullt'),
					indicator:'green'
				}, 2);
			});// , ("Utilities"));	
//$(".page-head-content")[0].children[1].children[1].children[1].attr("disabled",true)
		}
		else{
			frm.remove_custom_button('Create cost allocation');
		}
  }
});


frappe.ui.form.on("Fees", {

    fee_structure: function(frm) {
		frm.set_value("components" ,"");
		if (frm.doc.fee_structure) {
			frappe.call({
				method: "education.education.api.get_fee_components",
				args: {
					"fee_structure": frm.doc.fee_structure
				},
				callback: function(r) {
					if (r.message) {
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(frm.doc, "Fee Component", "components");
							row.fees_category = d.fees_category;
							row.description = d.description;
							row.amount = d.amount;
							row.fee_account = d.fee_account;
						});
					}
					refresh_field("components");
					frm.trigger("calculate_total_amount");
				}
			});
		}
	},
})