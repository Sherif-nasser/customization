import datetime
import json
from collections import defaultdict
from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry

import frappe
from frappe import scrub
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils import nowdate, unique
from frappe.model.document import Document

import erpnext
from erpnext.stock.get_item_details import _get_item_tax_template
from frappe.utils import cint, cstr, flt

@frappe.whitelist()
##Gets all data from the selected Payment Entry as a dictionary
def get_the_items_from_PaymentEntry(docname):
	PE = frappe.get_doc("Payment Entry", docname)
	values = PE.as_dict()
		
	return values


@frappe.whitelist()
## Returns all values from the selected Fees doctype related to the opend 
## Payment Entry
def get_the_items_from_feesDoc(docname):
	try:
		feeDoc = frappe.get_doc('Fees', docname) ##feeNames
		print(f'the fees doc is {feeDoc}')
		return feeDoc

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))



@frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
## Function that creates a JE from the information
## gathered from PE and Fees
def create_JornalEntry_from_PaymentEntry(docname):
	
	jornalDoc = frappe.new_doc('Journal Entry')

	itemsFromPE = get_the_items_from_PaymentEntry(docname)
	
	


	references = itemsFromPE.references
	reference = ""   ## Reference name of related PE down in the table
	for ref in references:
		if ref.reference_doctype ==  'Fees':
			reference = ref.reference_name
	itemsFromFees = get_the_items_from_feesDoc(reference).as_dict()
	

	jornalDoc.set('posting_date', datetime.date.today())
	jornalDoc.append('accounts', { ##set the calues account and debit at first place from payment entry
		'account': itemsFromFees.income_account,
		'debit_in_account_currency': itemsFromPE.paid_amount,
		# 'party_type': itemsFromPE.party_type,
		# 'party' : itemsFromPE.party,
	})
	jornalDoc.set('company', itemsFromFees.company)
	

	try:
	## Subtract values of the fees component [Balance] from total paid amount one by one
	## Check of result number negative or positive and calculate the remaining due ammount
		
		stopWhenNegative = True
		for component in itemsFromFees.components:
			updatedBalance = 0
			## if the result of paid amount is positive it adds the account 
			## with the ref amount as a row in JE and update the balance in the Fees table to 0
			if component.balance > 0 and stopWhenNegative == True:
				
				if itemsFromPE.paid_amount > component.balance:
					print(f"this is the paid amount in positive {itemsFromPE.paid_amount}")
					print("in positive")
					print(itemsFromPE.paid_amount)
					## Subtract the first balance from Fees references 
					subtractionResult = itemsFromPE.paid_amount - component.balance 
					print(subtractionResult)
					## updates the total paid amount 
					itemsFromPE.paid_amount = subtractionResult
					print(component.amount)
					jornalDoc.append('accounts', {
							'account': component.fee_account,
							'debit_in_account_currency':0,
							'credit_in_account_currency' : component.balance
					})
					# component.balance = updatedBalance
					print(f"this is the positive comp name{component.name}")
					frappe.db.set_value("Fee Component",component.name, 'balance', updatedBalance)
					component.balance = updatedBalance
					try:
						itemsFromFees.reload()
						print("reloaded maaaaaaate AHHAHAHAHAHAHAHAHAH")
					except Exception as e:
						print("NOOOOOOO")
						error_log = print(frappe.session.user,str(e))
			

				######################################################################################

				if itemsFromPE.paid_amount == component.balance:
					
					subtractionResult = itemsFromPE.paid_amount - component.balance 
					updatedBalance = subtractionResult
					print("in equals ")
					print(itemsFromPE.paid_amount)
					jornalDoc.append('accounts', {
							'account': component.fee_account,
							'debit_in_account_currency':0,
							'credit_in_account_currency' : component.balance
					})
					stopWhenNegative = False
					# component.balance = updatedBalance
					print(f"this is the equals comp name{component.name}")
					frappe.db.set_value("Fee Component",component.name, 'balance', updatedBalance)
					component.balance = updatedBalance	
					try:
						itemsFromFees.reload()
						print("reloaded maaaaaaate AHHAHAHAHAHAHAHAHAH")
					except Exception as e:
						print("NOOOOOOO")
						error_log = print(frappe.session.user,str(e))

				######################################################################################

			## if the result of paid amount is negative it adds the negative paid amount 
			# to the total amount of Fees.ref to get the remainig due amount
			# Then it updates the balance of the remaining in the row for the second payment  
			#finally it adds the final row in JE to equalize the debit and credit amount
			# paid amount - category balance = (-) remaining amount of the category fees
			# - remaining amount of the category fees + category amount = the new category amount 
				if  itemsFromPE.paid_amount < component.balance:
					print(f"this is the paid amount in negative {itemsFromPE.paid_amount}")
					subtractionResult = itemsFromPE.paid_amount - component.balance  ##-100
					updatedBalance = abs(subtractionResult)
					print("in negative")
					# print(updatedBalance)
					print(itemsFromPE.paid_amount)
					print(component.balance) 
					print(component.amount)
					jornalDoc.append('accounts', {
							'account': component.fee_account,
							'debit_in_account_currency':0,
							'credit_in_account_currency' : itemsFromPE.paid_amount
						})

					stopWhenNegative = False
					# component.balance = updatedBalance
					print(stopWhenNegative)
					print(f"this is the minus comp name{component.name}")
				
					frappe.db.set_value("Fee Component",component.name, 'balance', updatedBalance)
					component.balance = updatedBalance		
					try:
						itemsFromFees.reload()
						print("reloaded maaaaaaate AHHAHAHAHAHAHAHAHAH")
					except Exception as e:
						print("NOOOOOOO")
						error_log = print(frappe.session.user,str(e))
			
			
		######################################################################################	
	except Exception as e:
		error_log = print(frappe.session.user,str(e))

	
	jornalDoc.save()
	return jornalDoc.submit()

# list(word_freq.values())[0]


